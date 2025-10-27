import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def _get_token():
    resp = client.post("/auth/signup", json={"email": "x@y.com", "password": "pw"})
    assert resp.status_code == 200
    return resp.json()["access_token"]


def _create_analysis(token):
    # Reuse analyze endpoint to create an analysis row
    csv_content = "date,value\n2024-01-01,10\n2024-01-02,20\n"
    files = {"file": ("data.csv", csv_content, "text/csv")}
    resp = client.post("/analyze/", files=files, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    return resp.json()["analysis_id"]


def test_explain_flow():
    token = _get_token()
    analysis_id = _create_analysis(token)
    resp = client.post("/explain/", json={"analysis_id": analysis_id}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["explanations"]


def test_forecast_flow():
    token = _get_token()
    analysis_id = _create_analysis(token)
    resp = client.post("/forecast/", json={"analysis_id": analysis_id, "days": 7}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["forecast"]["forecast"]["dates"]
