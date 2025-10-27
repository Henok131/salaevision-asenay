import pytest
import httpx
from fastapi import FastAPI, HTTPException
from routers import tokens as tokens_router
from routers import consent as consent_router

@pytest.mark.asyncio
async def test_invalid_jwt_status():
    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code in (401, 403)

@pytest.mark.asyncio
async def test_valid_jwt_status(monkeypatch):
    async def mock_verify(token):
        return {"id": "user_a"}
    monkeypatch.setattr(tokens_router, "verify_token", mock_verify)

    async def mock_get(uid: str):
        return {"plan": "free", "total_tokens": 100, "used_tokens": 10, "last_used": None}
    monkeypatch.setattr(tokens_router, "_get_or_create_token_row", mock_get)

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status", headers={"Authorization": "Bearer any"})
        assert resp.status_code == 200
        assert resp.json()["remaining_tokens"] == 90

@pytest.mark.asyncio
async def test_cross_user_access_forbidden(monkeypatch):
    async def mock_verify(token):
        return {"id": "user_b"}
    monkeypatch.setattr(tokens_router, "verify_token", mock_verify)

    async def mock_get(uid: str):
        # Simulate RLS policy: only allow user_a rows
        if uid != "user_a":
            raise HTTPException(status_code=403, detail="RLS forbidden")
        return {"plan": "free", "total_tokens": 100, "used_tokens": 10, "last_used": None}
    monkeypatch.setattr(tokens_router, "_get_or_create_token_row", mock_get)

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status", headers={"Authorization": "Bearer token_user_a"})
        assert resp.status_code == 403
