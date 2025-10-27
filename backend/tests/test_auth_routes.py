import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_signup_and_login_flow():
    # Signup
    resp = client.post("/auth/signup", json={"email": "user@example.com", "password": "pass1234"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    token = data["access_token"]

    # Get current user
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["user"]["email"] == "user@example.com"

    # Refresh token
    resp = client.post("/auth/refresh", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
