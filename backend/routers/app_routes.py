from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from logging import getLogger
from datetime import datetime, timedelta
from PIL import Image
import base64
import io
import os

from services.supabase_client import get_supabase_client, get_supabase_admin_client

logger = getLogger("salesvision")

router = APIRouter()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or str(value).strip() == "":
        raise HTTPException(status_code=500, detail=f"Missing environment: {name}")
    return value


@router.get("/config")
async def get_config():
    return {
        "site_url": _require_env("SITE_URL"),
        "domain": _require_env("DOMAIN"),
        "from_email": _require_env("FROM_EMAIL"),
        "rate_limit_usage": int(_require_env("RATE_LIMIT_USAGE")),
        "openai_timeout_seconds": int(_require_env("OPENAI_TIMEOUT_SECONDS")),
        "integrations": {
            "sap": os.getenv("ENABLE_SAP", "false").lower() == "true",
            "hubspot": os.getenv("ENABLE_HUBSPOT", "false").lower() == "true",
            "drive": os.getenv("ENABLE_DRIVE", "false").lower() == "true",
            "slack": False,
            "gmail": False,
        },
    }


@router.get("/customer_profile/{customer_id}")
async def customer_profile(customer_id: str):
    logger.info(f"customer_profile requested id={customer_id}")
    supabase = get_supabase_client()
    try:
        result = (
            supabase.table("users")
            .select("id,email,plan,created_at")
            .eq("id", customer_id)
            .execute()
        )
        if result.data:
            row = result.data[0]
            profile = {
                "id": row.get("id", customer_id),
                "email": row.get("email", "unknown@example.com"),
                "plan": row.get("plan", "free"),
                "created_at": row.get("created_at"),
                "lifetime_value": 12500.0,
                "score": 0.82,
            }
        else:
            profile = {
                "id": customer_id,
                "email": f"lead+{customer_id}@example.com",
                "plan": "free",
                "created_at": datetime.utcnow().isoformat(),
                "lifetime_value": 3400.0,
                "score": 0.67,
            }
        logger.info(f"customer_profile success id={customer_id}")
        return profile
    except Exception as e:
        logger.exception("customer_profile failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload_invoice/{customer_id}")
async def upload_invoice(customer_id: str, file: UploadFile = File(...)):
    logger.info(f"upload_invoice start id={customer_id} filename={file.filename}")
    bucket = _require_env("STORAGE_INVOICE_BUCKET")
    try:
        admin = get_supabase_admin_client()
        content = await file.read()
        path = f"{customer_id}/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{file.filename}"
        admin.storage.from_(bucket).upload(path, content)
        preview_b64 = None
        if file.content_type and file.content_type.startswith("image/"):
            try:
                img = Image.open(io.BytesIO(content))
                img.thumbnail((320, 320))
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                preview_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            except Exception:
                preview_b64 = None
        response = {
            "path": path,
            "bucket": bucket,
            "size": len(content),
            "content_type": file.content_type,
            "preview_png_base64": preview_b64,
        }
        logger.info(f"upload_invoice success id={customer_id} path={path}")
        return response
    except Exception as e:
        logger.exception("upload_invoice failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.post("/search_leads")
async def search_leads(query: str = Form(...)):
    logger.info(f"search_leads query='{query[:40]}'")
    try:
        results = [
            {"id": "lead-101", "score": 0.93, "name": "Acme Corp", "reason": "High similarity to past won deals"},
            {"id": "lead-202", "score": 0.88, "name": "Globex", "reason": "Matching industry and company size"},
        ]
        logger.info(f"search_leads success count={len(results)}")
        return {"results": results}
    except Exception as e:
        logger.exception("search_leads failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendation/{lead_id}")
async def recommendation(lead_id: str):
    logger.info(f"recommendation for lead_id={lead_id}")
    try:
        recs = [
            {
                "title": "Personalized outreach",
                "body": "Send a tailored email referencing recent industry trends.",
                "confidence": 0.86,
            },
            {
                "title": "Offer pilot",
                "body": "Propose a 2-week pilot with clear KPIs.",
                "confidence": 0.81,
            },
        ]
        return {"lead_id": lead_id, "recommendations": recs}
    except Exception as e:
        logger.exception("recommendation failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/integrations/status")
async def integrations_status(provider: str):
    flags = {
        "sap": os.getenv("ENABLE_SAP", "false").lower() == "true",
        "hubspot": os.getenv("ENABLE_HUBSPOT", "false").lower() == "true",
        "drive": os.getenv("ENABLE_DRIVE", "false").lower() == "true",
        "slack": False,
        "gmail": False,
    }
    enabled = flags.get(provider.lower())
    if enabled is None:
        raise HTTPException(status_code=404, detail="Unknown provider")
    status = {
        "provider": provider,
        "enabled": enabled,
        "connected": False,
        "last_checked": datetime.utcnow().isoformat(),
    }
    logger.info(f"integrations_status provider={provider} enabled={enabled}")
    return status


@router.post("/integrations/connect")
async def integrations_connect(provider: str = Form(...)):
    token = os.getenv("WEBHOOK_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="WEBHOOK_TOKEN not set")
    logger.info(f"integrations_connect provider={provider}")
    return {
        "provider": provider,
        "connected": True,
        "connection_id": f"demo-{provider}-{int(datetime.utcnow().timestamp())}",
    }


@router.get("/funnel-stats")
async def funnel_stats():
    data = {
        "stages": ["Visited", "Qualified", "Demo", "Proposal", "Closed Won"],
        "counts": [1200, 450, 220, 140, 65],
        "conversion_rates": [1.0, 0.375, 0.489, 0.636, 0.464],
        "period": "last_30_days",
    }
    logger.info("funnel-stats served")
    return data


@router.get("/usage/history")
async def usage_history():
    today = datetime.utcnow().date()
    series = []
    for i in range(14):
        d = today - timedelta(days=13 - i)
        series.append({"date": d.isoformat(), "requests": 10 + (i * 3)})
    logger.info("usage/history served")
    return {"series": series}


@router.post("/webhook/event")
async def webhook_event(request: Request):
    token = request.headers.get("X-Webhook-Token") or request.query_params.get("token")
    expected = os.getenv("WEBHOOK_TOKEN")
    if not expected:
        raise HTTPException(status_code=500, detail="WEBHOOK_TOKEN not set")
    if token != expected:
        logger.warning("webhook_event invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")
    try:
        body = await request.json()
    except Exception:
        body = {}
    logger.info(f"webhook_event received type={body.get('type','unknown')}")
    return {"received": True}
