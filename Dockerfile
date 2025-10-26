# =========================
# Frontend build stage
# =========================
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ .
RUN npm run build

# =========================
# Backend runtime stage
# =========================
FROM python:3.11-slim AS backend
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*
# Python deps (env-only configuration; code is not changed post-build)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    "supabase==2.*" \
    sendgrid==6.* \
    "openai==1.*" \
    slowapi==0.1.* \
    python-dotenv==1.* \
    sentry-sdk==1.* \
    APScheduler==3.* \
    pydantic==2.* \
    requests==2.*
# App code
COPY src/ /app/src/
# Logs directory
RUN mkdir -p /logs
EXPOSE 8080
# Note: API_HOST and API_PORT pulled from .env via docker-compose env_file
CMD ["sh", "-c", "uvicorn src.main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8080}"]

# =========================
# Nginx static stage (serves frontend)
# =========================
FROM nginx:alpine AS nginx-static
# Copy built frontend to nginx html
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html
# Nginx will receive its conf at runtime via mounted template and envsubst
