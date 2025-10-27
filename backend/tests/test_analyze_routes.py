import io
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _get_token():
    resp = client.post("/auth/signup", json={"email": "a@b.com", "password": "x"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_analyze_upload_and_store():
    token = _get_token()
    csv_content = "date,value\n2024-01-01,10\n2024-01-02,20\n"
    files = {"file": ("data.csv", csv_content, "text/csv")}
    resp = client.post("/analyze/", files=files, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["insights"]
