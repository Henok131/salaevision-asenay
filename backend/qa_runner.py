import os
import io
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

import httpx
from PIL import Image


def require_env(name: str) -> str:
    v = os.getenv(name)
    if v is None or str(v).strip() == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v


def configure_logger() -> logging.Logger:
    log_file = require_env("LOG_FILE")
    logger = logging.getLogger("salesvision.qa")
    logger.setLevel(logging.INFO)
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2)
        fmt = logging.Formatter(
            fmt="%Y-%m-%dT%H:%M:%S%z %(levelname)s %(name)s %(message)s",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


async def run_tests():
    logger = configure_logger()
    site_url = require_env("SITE_URL").rstrip("/")
    base = f"{site_url}/api"
    timeout = int(require_env("OPENAI_TIMEOUT_SECONDS"))
    token = os.getenv("WEBHOOK_TOKEN", "")

    async with httpx.AsyncClient(timeout=timeout) as client:
        async def hit(method: str, path: str, **kwargs):
            url = f"{base}{path}"
            try:
                resp = await client.request(method, url, **kwargs)
                ok = 200 <= resp.status_code < 300
                logger.info(f"QA {method} {path} status={resp.status_code} ok={ok}")
                return ok, resp
            except Exception as e:
                logger.error(f"QA {method} {path} error={e}")
                return False, None

        await hit("GET", "/health")

        # /webhook/event
        await hit("POST", f"/webhook/event?token={token}", json={"type": "qa.test", "time": datetime.utcnow().isoformat()})

        # /customer_profile/{id}
        await hit("GET", "/customer_profile/demo-user-1")

        # /upload_invoice/{id}
        # create tiny PNG in memory
        img = Image.new("RGB", (20, 20), (123, 222, 111))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        files = {"file": ("invoice.png", buf.getvalue(), "image/png")}
        await hit("POST", "/upload_invoice/demo-user-1", files=files)

        # /search_leads
        data = {"query": "enterprise retail leads in EU"}
        await hit("POST", "/search_leads", data=data)

        # /recommendation/{id}
        await hit("GET", "/recommendation/lead-101")

        # /integrations/status
        await hit("GET", "/integrations/status", params={"provider": "sap"})

        # /integrations/connect
        await hit("POST", "/integrations/connect", data={"provider": "sap"})

        # /funnel-stats
        await hit("GET", "/funnel-stats")

        # /usage/history
        await hit("GET", "/usage/history")

        # /config (optional)
        await hit("GET", "/config")


if __name__ == "__main__":
    asyncio.run(run_tests())
