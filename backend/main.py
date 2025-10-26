from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from routers import analyze, forecast, explain, auth, stripe_webhook
from services.database import init_db

load_dotenv()


def require_env(var_names: list[str]) -> dict[str, str]:
    """Fetch required env vars; raise if any missing or empty."""
    values: dict[str, str] = {}
    missing: list[str] = []
    for name in var_names:
        val = os.getenv(name)
        if val is None or str(val).strip() == "":
            missing.append(name)
        else:
            values[name] = val
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
    return values


def configure_logging() -> logging.Logger:
    """Configure application logger to write to LOG_FILE with rotation."""
    env = require_env(["LOG_FILE"])
    log_path = Path(env["LOG_FILE"]).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("salesvision")
    logger.setLevel(logging.INFO)
    # Avoid duplicate handlers during reloads
    if not any(isinstance(h, RotatingFileHandler) for h in logger.handlers):
        handler = RotatingFileHandler(
            log_path, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Strict env validation
    required = [
        # Supabase and auth
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "JWT_SECRET_KEY",
        # OpenAI and limits
        "OPENAI_API_KEY",
        "OPENAI_TIMEOUT_SECONDS",
        "RATE_LIMIT_USAGE",
        # App/site
        "SITE_URL",
        "DOMAIN",
        "FROM_EMAIL",
        # Storage and integrations
        "STORAGE_INVOICE_BUCKET",
        "ENABLE_DRIVE",
        "GOOGLE_SERVICE_ACCOUNT_JSON",
        "ENABLE_SAP",
        "ENABLE_HUBSPOT",
        "WEBHOOK_TOKEN",
        # Logging
        "LOG_FILE",
    ]
    require_env(required)

    # Configure logging
    logger = configure_logging()
    logger.info("Startup: SalesVision API initializing")

    # Startup
    await init_db()
    try:
        yield
    finally:
        logger.info("Shutdown: SalesVision API stopping")


app = FastAPI(
    title="SalesVision AI API",
    description="AI-powered sales analytics and forecasting API",
    version="1.0.0",
    lifespan=lifespan,
)


# CORS middleware - only allow SITE_URL from env (no fallbacks)
cors_env = require_env(["SITE_URL"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=[cors_env["SITE_URL"]],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security
security = HTTPBearer()


# Request/response logging middleware
logger = configure_logging()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        f"request start method={request.method} path={request.url.path} client={request.client.host if request.client else 'unknown'}"
    )
    response = await call_next(request)
    logger.info(
        f"request end method={request.method} path={request.url.path} status={response.status_code}"
    )
    return response


# Include routers
from routers import app_routes  # noqa: E402

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecasting"])
app.include_router(explain.router, prefix="/explain", tags=["explainability"])
app.include_router(stripe_webhook.router, prefix="/stripe", tags=["payments"])
app.include_router(app_routes.router, tags=["app"])


@app.get("/")
async def root():
    return {
        "message": "SalesVision AI API",
        "version": "1.0.0",
        "status": "healthy",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SalesVision AI API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

