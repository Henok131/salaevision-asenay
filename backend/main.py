from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from routers import analyze, forecast, explain, auth, stripe_webhook
from routers import ocr
from routers import embed
from routers import orgs
from routers import dashboards
from routers import plugins
from routers import insights
from routers import dashboards
from services.database import init_db
from services.digest import run_weekly_digest_job
from services.supabase_client import get_supabase_client

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Schedule weekly digest (every Monday 08:00 UTC)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_weekly_digest_job, CronTrigger(day_of_week='mon', hour=8, minute=0))
    scheduler.start()
    yield
    # Shutdown
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass

app = FastAPI(
    title="SalesVision AI API",
    description="AI-powered sales analytics and forecasting API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://salesvision-ai.vercel.app",
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecasting"])
app.include_router(explain.router, prefix="/explain", tags=["explainability"])
app.include_router(stripe_webhook.router, prefix="/stripe", tags=["payments"])
app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
app.include_router(embed.router, prefix="/embed", tags=["embed"])
app.include_router(orgs.router, prefix="/orgs", tags=["organizations"])
app.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])
app.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(dashboards.router, prefix="/dashboards", tags=["dashboards"])

@app.get("/")
async def root():
    return {
        "message": "SalesVision AI API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SalesVision AI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

