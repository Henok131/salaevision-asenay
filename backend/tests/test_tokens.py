import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_token_status_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status")
        assert resp.status_code == 403 or resp.status_code == 401

@pytest.mark.asyncio
async def test_token_status_mocked(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    from services import auth as auth_service
    monkeypatch.setattr(auth_service, "verify_token", mock_verify)

    class MockTable:
        def __init__(self):
            self._row = None
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

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/api/token/status", headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert "remaining_tokens" in data
        assert data["total_tokens"] == 1000

@pytest.mark.asyncio
async def test_token_consume_under_limit(monkeypatch):
    async def mock_verify(token):
        return {"id": "00000000-0000-0000-0000-000000000000"}
    from services import auth as auth_service
    monkeypatch.setattr(auth_service, "verify_token", mock_verify)

    class MockTable:
        def __init__(self):
            self._used = 10
            self._row = {"id": "000...", "plan": "free", "total_tokens": 1000, "used_tokens": self._used}
        def select(self, *_args, **_kwargs):
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        @property
                        def data(self):
                            return [self._row]
                    return E()
            return R()
        def insert(self, obj):
            class E:
                @property
                def data(self):
                    return [obj]
            return E()
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

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/token/consume", json={"amount": 1}, headers={"Authorization": "Bearer x"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["used_tokens"] >= 11
        assert data["remaining_tokens"] == data["total_tokens"] - data["used_tokens"]

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
            class R:
                def eq(self, *_a, **_k):
                    class E:
                        @property
                        def data(self):
                            return [self._row]
                    return E()
            return R()
        def insert(self, obj):
            class E:
                @property
                def data(self):
                    return [obj]
            return E()
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

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post("/api/token/consume", json={"amount": 1}, headers={"Authorization": "Bearer x"})
        assert resp.status_code == 403
