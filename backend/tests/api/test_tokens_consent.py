import os
import sys
from types import SimpleNamespace
from unittest.mock import patch
import pytest
import httpx

# Ensure import of backend.main
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.main import app  # noqa: E402


def _token_prefix() -> str:
    paths = {getattr(r, 'path', '') for r in app.routes}
    return '/api/token' if any(p.startswith('/api/token') for p in paths) else '/tokens'


def _user_prefix() -> str:
    paths = {getattr(r, 'path', '') for r in app.routes}
    return '/api/user' if any(p.startswith('/api/user') for p in paths) else '/user'


class _MockTable:
    def __init__(self, name: str, dataset: dict):
        self._name = name
        self._dataset = dataset
        self._op = None
        self._obj = None
    def select(self, *_a, **_k):
        self._op = 'select'
        return self
    def insert(self, obj):
        self._op = 'insert'
        self._obj = obj
        return self
    def update(self, obj):
        self._op = 'update'
        self._obj = obj
        return self
    def eq(self, *_a, **_k):
        return self
    def execute(self):
        if self._op == 'select':
            data = self._dataset.get(self._name, [])
        elif self._op == 'insert':
            data = self._dataset.get(self._name, [self._obj or {}])
        else:
            data = self._dataset.get(self._name, [self._obj or {}])
        return SimpleNamespace(data=data)


class _MockSupabase:
    def __init__(self, dataset: dict):
        self._dataset = dataset
    def table(self, name: str):
        return _MockTable(name, self._dataset)


def _auth_header():
    return {"Authorization": "Bearer test"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_status_success():
    dataset = {
        'token_usage': [{'id': 'user_1', 'plan': 'free', 'total_tokens': 100, 'used_tokens': 10, 'last_used': None}],
    }

    async def mock_verify(_):
        return {'id': 'user_1'}

    from routers import tokens as tokens_router

    transport = httpx.ASGITransport(app=app)
    with (
        patch('backend.main.init_db', new=lambda *_a, **_k: None),
        patch.object(tokens_router, 'verify_token', new=mock_verify),
        patch.object(tokens_router, 'get_supabase_client', return_value=_MockSupabase(dataset)),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.get(f"{_token_prefix()}/status", headers=_auth_header())
            assert resp.status_code == 200
            data = resp.json()
            assert data['plan'] == 'free'
            assert data['remaining_tokens'] == 90


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_consume_under_limit():
    dataset = {
        'token_usage': [{'id': 'user_1', 'plan': 'free', 'total_tokens': 10, 'used_tokens': 5, 'last_used': None}],
    }

    async def mock_verify(_):
        return {'id': 'user_1'}

    class _Update:
        def __init__(self, obj, base):
            self._obj = obj
            self._base = base
        def eq(self, *_a, **_k):
            merged = {**self._base, **self._obj}
            class _E:
                def __init__(self, obj):
                    self._obj = obj
                @property
                def data(self):
                    return [self._obj]
                def execute(self):
                    return self
            return _E(merged)

    class _TableC(_MockTable):
        def update(self, obj):
            self._op = 'update'
            return _Update(obj, self._dataset.get(self._name, [{}])[0])

    class _SupabaseC(_MockSupabase):
        def table(self, name: str):
            return _TableC(name, self._dataset)

    from routers import tokens as tokens_router

    transport = httpx.ASGITransport(app=app)
    with (
        patch('backend.main.init_db', new=lambda *_a, **_k: None),
        patch.object(tokens_router, 'verify_token', new=mock_verify),
        patch.object(tokens_router, 'get_supabase_client', return_value=_SupabaseC(dataset)),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f"{_token_prefix()}/consume", json={'amount': 2}, headers=_auth_header())
            assert resp.status_code == 200
            data = resp.json()
            assert data['used_tokens'] == 7
            assert data['remaining_tokens'] == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_token_consume_over_limit():
    dataset = {
        'token_usage': [{'id': 'user_1', 'plan': 'free', 'total_tokens': 1, 'used_tokens': 1, 'last_used': None}],
    }

    async def mock_verify(_):
        return {'id': 'user_1'}

    from routers import tokens as tokens_router

    class DummyTable:
        def select(self, *_a, **_k):
            return self
        def insert(self, *_a, **_k):
            # Simulate creating a default row so insert.execute().data[0] exists
            class _Exec:
                def __init__(self):
                    self.data = [{'id': 'user_1', 'plan': 'free', 'total_tokens': 1, 'used_tokens': 1}]
                def execute(self):
                    return self
            return _Exec()
        def update(self, *_a, **_k):
            return self
        def eq(self, *_a, **_k):
            return self
        def execute(self):
            return SimpleNamespace(data=[])

    class DummySupabase:
        def table(self, _):
            return DummyTable()

    transport = httpx.ASGITransport(app=app)
    with (
        patch('backend.main.init_db', new=lambda *_a, **_k: None),
        patch.object(tokens_router, 'verify_token', new=mock_verify),
        patch.object(tokens_router, 'get_supabase_client', return_value=DummySupabase()),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f"{_token_prefix()}/consume", json={'amount': 1}, headers=_auth_header())
            assert resp.status_code == 403


@pytest.mark.unit
@pytest.mark.asyncio
async def test_user_consent_success():
    dataset = {}

    async def mock_verify(_):
        return {'id': 'user_1'}

    class _TableU(_MockTable):
        def update(self, obj):
            class _E:
                def eq(self, *_a, **_k):
                    class _R:
                        def execute(self):
                            return None
                    return _R()
            return _E()

    class _SupabaseU(_MockSupabase):
        def table(self, name: str):
            return _TableU(name, self._dataset)

    from routers import consent as consent_router

    transport = httpx.ASGITransport(app=app)
    with (
        patch('backend.main.init_db', new=lambda *_a, **_k: None),
        patch.object(consent_router, 'verify_token', new=mock_verify),
        patch.object(consent_router, 'get_supabase_client', return_value=_SupabaseU(dataset)),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f"{_user_prefix()}/consent", headers=_auth_header())
            assert resp.status_code == 200
            data = resp.json()
            assert data['success'] is True
            assert data['consent_given'] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auth_policy_invalid_token():
    from routers import tokens as tokens_router

    async def mock_verify(_):
        return None  # invalid

    transport = httpx.ASGITransport(app=app)
    with patch.object(tokens_router, 'verify_token', new=mock_verify):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.get(f"{_token_prefix()}/status", headers=_auth_header())
            assert resp.status_code in (401, 403)
