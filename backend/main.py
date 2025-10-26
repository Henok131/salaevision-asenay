from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

from routers import analyze, forecast, explain, auth, stripe_webhook
from routers import tokens
from services.database import init_db
from services.supabase_client import get_supabase_client

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="SalesVision AI API",
    description="AI-powered sales analytics and forecasting API",
    version="1.0.0",
    lifespan=lifespan
)

# Logging setup
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)
log_path = os.path.join(logs_dir, 'system.log')
handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("uvicorn.error")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
app.include_router(forecast.router, prefix="/forecast", tags=["forecasting"])
app.include_router(explain.router, prefix="/explain", tags=["explainability"])
app.include_router(stripe_webhook.router, prefix="/stripe", tags=["payments"])
app.include_router(tokens.router, prefix="/tokens", tags=["tokens"])
# API aliases with /api prefix for compatibility
app.include_router(tokens.router, prefix="/api/token", tags=["tokens"])

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

