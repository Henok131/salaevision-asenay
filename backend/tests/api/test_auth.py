import types
import pytest
import httpx
from fastapi import FastAPI
from routers import auth as auth_router


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_success(monkeypatch, supabase_factory):
    # Prepare mock Supabase client with successful sign-in
    user = types.SimpleNamespace(id='user_1', email='u@example.com', created_at='2024-01-01T00:00:00Z')
    supabase = supabase_factory(auth_sign_in_user=user)
    monkeypatch.setattr(auth_router, 'get_supabase_client', lambda: supabase)

    app = FastAPI()
    app.include_router(auth_router.router, prefix='/auth')
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        resp = await ac.post('/auth/login', json={'email': 'u@example.com', 'password': 'x'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['token_type'] == 'bearer'
        assert data['user']['email'] == 'u@example.com'
        assert 'access_token' in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_invalid_credentials(monkeypatch, supabase_factory):
    # sign_in_with_password returns user=None
    supabase = supabase_factory(auth_sign_in_user=None)
    monkeypatch.setattr(auth_router, 'get_supabase_client', lambda: supabase)

    app = FastAPI()
    app.include_router(auth_router.router, prefix='/auth')
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        resp = await ac.post('/auth/login', json={'email': 'bad@example.com', 'password': 'wrong'})
        assert resp.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_signup_success(monkeypatch, supabase_factory):
    user = types.SimpleNamespace(id='user_2', email='new@example.com', created_at='2024-01-01T00:00:00Z')
    # Configure supabase to return a user on sign_up and allow insert into users table
    supabase = supabase_factory(
        auth_sign_up_user=user,
        insert_map={'users': [{'id': 'user_2'}]},
    )
    monkeypatch.setattr(auth_router, 'get_supabase_client', lambda: supabase)

    app = FastAPI()
    app.include_router(auth_router.router, prefix='/auth')
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        resp = await ac.post('/auth/signup', json={'email': 'new@example.com', 'password': 'pw', 'full_name': 'New User'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['user']['email'] == 'new@example.com'
        assert data['token_type'] == 'bearer'


@pytest.mark.unit
@pytest.mark.asyncio
async def test_me_and_refresh(monkeypatch, valid_user):
    async def mock_verify(token: str):
        return valid_user

    monkeypatch.setattr(auth_router, 'verify_token', mock_verify)

    app = FastAPI()
    app.include_router(auth_router.router, prefix='/auth')
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        # /me
        r1 = await ac.get('/auth/me', headers={'Authorization': 'Bearer t'})
        assert r1.status_code == 200
        assert r1.json()['user']['id'] == valid_user['id']

        # /refresh
        r2 = await ac.post('/auth/refresh', headers={'Authorization': 'Bearer t'})
        assert r2.status_code == 200
        assert 'access_token' in r2.json()
