import pytest
import httpx
from fastapi import FastAPI
from routers import tokens as tokens_router
from routers import consent as consent_router

@pytest.mark.asyncio
async def test_token_status_unauthorized():
    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status")
        assert resp.status_code in (401, 403)

@pytest.mark.asyncio
async def test_token_status_mocked(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    monkeypatch.setattr(tokens_router, "verify_token", mock_verify)

    async def mock_get_or_create(uid: str):
        return {"plan": "free", "total_tokens": 1000, "used_tokens": 0, "last_used": None}
    monkeypatch.setattr(tokens_router, "_get_or_create_token_row", mock_get_or_create)

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status", headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_tokens"] == 1000
        assert "remaining_tokens" in data

@pytest.mark.asyncio
async def test_token_consume_under_limit(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    monkeypatch.setattr(tokens_router, "verify_token", mock_verify)

    async def mock_get_or_create(uid: str):
        return {"plan": "free", "total_tokens": 10, "used_tokens": 5, "last_used": None}
    monkeypatch.setattr(tokens_router, "_get_or_create_token_row", mock_get_or_create)

    class E:
        def __init__(self, obj):
            self._obj = obj
        @property
        def data(self):
            return [self._obj]
        def execute(self):
            return self

    class MockUpdate:
        def __init__(self, obj):
            self.obj = obj
        def eq(self, *_a, **_k):
            return E(self.obj)

    class MockTable:
        def update(self, obj):
            return MockUpdate(obj)

    class MockSupabase:
        def table(self, _):
            return MockTable()

    monkeypatch.setattr(tokens_router, "get_supabase_client", lambda: MockSupabase())

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/token/consume", json={"amount": 2}, headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["used_tokens"] == 7
        assert data["remaining_tokens"] == 3

@pytest.mark.asyncio
async def test_token_consume_over_limit(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    monkeypatch.setattr(tokens_router, "verify_token", mock_verify)

    async def mock_get_or_create(uid: str):
        return {"plan": "free", "total_tokens": 1, "used_tokens": 1, "last_used": None}
    monkeypatch.setattr(tokens_router, "_get_or_create_token_row", mock_get_or_create)

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/token/consume", json={"amount": 1}, headers={"Authorization": "Bearer x"})
        assert resp.status_code == 403

@pytest.mark.asyncio
async def test_user_consent(monkeypatch):
    from routers import consent as consent_router

    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    monkeypatch.setattr(consent_router, "verify_token", mock_verify)

    class MockTable:
        def update(self, obj):
            class R:
                def eq(self, *_a, **_k):
                    class E2:
                        def execute(self):
                            return None
                    return E2()
            return R()
    class MockSupabase:
        def table(self, _):
            return MockTable()

    monkeypatch.setattr(consent_router, "get_supabase_client", lambda: MockSupabase())

    app = FastAPI()
    app.include_router(consent_router.router, prefix="/api/user")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/user/consent", headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["consent_given"] is True
