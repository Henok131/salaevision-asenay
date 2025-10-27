import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from routers import tokens as tokens_router
from routers import consent as consent_router

@pytest.mark.asyncio
async def test_token_status_unauthorized():
    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status")
        assert resp.status_code in (401, 403)

@pytest.mark.asyncio
async def test_token_status_mocked(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    from services import auth as auth_service
    monkeypatch.setattr(auth_service, "verify_token", mock_verify)

    class MockTable:
        def select(self, *_args, **_kwargs):
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        @property
                        def data(self):
                            return []
                    return E()
            return R()
        def insert(self, obj):
            class E:
                @property
                def data(self):
                    return [obj]
            return E()
    class MockSupabase:
        def table(self, _):
            return MockTable()

    from services import supabase_client
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: MockSupabase())

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status", headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_tokens"] == 1000
        assert "remaining_tokens" in data

@pytest.mark.asyncio
async def test_token_consume_under_limit(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    from services import auth as auth_service
    monkeypatch.setattr(auth_service, "verify_token", mock_verify)

    class MockTable:
        def __init__(self):
            self._row = {"id": "000...", "plan": "free", "total_tokens": 10, "used_tokens": 5}
        def select(self, *_args, **_kwargs):
            row = self._row
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        @property
                        def data(self):
                            return [row]
                    return E()
            return R()
        def update(self, obj):
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        @property
                        def data(self):
                            return [obj]
                    return E()
            return R()
    class MockSupabase:
        def table(self, _):
            return MockTable()

    from services import supabase_client
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: MockSupabase())

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/token/consume", json={"amount": 2}, headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["used_tokens"] == 7
        assert data["remaining_tokens"] == 3

@pytest.mark.asyncio
async def test_token_consume_over_limit(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    from services import auth as auth_service
    monkeypatch.setattr(auth_service, "verify_token", mock_verify)

    class MockTable:
        def __init__(self):
            self._row = {"id": "000...", "plan": "free", "total_tokens": 1, "used_tokens": 1}
        def select(self, *_args, **_kwargs):
            row = self._row
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        @property
                        def data(self):
                            return [row]
                    return E()
            return R()
    class MockSupabase:
        def table(self, _):
            return MockTable()

    from services import supabase_client
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: MockSupabase())

    app = FastAPI()
    app.include_router(tokens_router.router, prefix="/api/token")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/token/consume", json={"amount": 1}, headers={"Authorization": "Bearer x"})
        assert resp.status_code == 403

@pytest.mark.asyncio
async def test_user_consent(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    from services import auth as auth_service
    monkeypatch.setattr(auth_service, "verify_token", mock_verify)

    class MockTable:
        def update(self, obj):
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        def execute(self):
                            return None
                    return E()
            return R()
    class MockSupabase:
        def table(self, _):
            return MockTable()

    from services import supabase_client
    monkeypatch.setattr(supabase_client, "get_supabase_client", lambda: MockSupabase())

    app = FastAPI()
    app.include_router(consent_router.router, prefix="/api/user")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/user/consent", headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["consent_given"] is True
