import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import sentry_sdk

from routes.auth import router as auth_router
from routes.leads import router as leads_router
from routes.usage import router as usage_router
from routes.email import router as email_router
from utils.ratelimit import limiter
from utils.logger import configure_logging

load_dotenv()

SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=0.1)

app = FastAPI(title="Lead CRM & Analytics API", version="1.0.0")
app.state.limiter = limiter

CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN] if CORS_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    retry = int(getattr(exc, "retry_after", 60))
    return JSONResponse(status_code=429, content={"error": "Rate limit exceeded", "retry_after": retry})


@app.get("/health")
async def health():
    return {"status": "ok", "service": "crm-analytics"}


# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(leads_router, prefix="/leads", tags=["leads"])
app.include_router(email_router, prefix="/email", tags=["email"])
app.include_router(usage_router, prefix="/usage", tags=["usage"])


# Initialize logging
configure_logging()
