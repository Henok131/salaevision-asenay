from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables BEFORE importing modules that read them at import-time
load_dotenv()

from routers import analyze, forecast, explain, auth, stripe_webhook
from services.database import init_db
from services.supabase_client import get_supabase_client

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

# CORS middleware (configurable via env)
# Provide a comma-separated list of origins in CORS_ALLOW_ORIGINS.
# For backward compatibility, FRONTEND_URL is used if CORS_ALLOW_ORIGINS is not set.
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if cors_origins_env:
    allow_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
else:
    fallback_frontend_url = os.getenv("FRONTEND_URL")
    allow_origins = [fallback_frontend_url] if fallback_frontend_url else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
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

