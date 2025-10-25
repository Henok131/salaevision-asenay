import io
import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "SalesVision AI API"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_auth_me_unauthorized():
    # Without auth header should be unauthorized
    response = client.get("/auth/me")
    assert response.status_code in (401, 403)


def test_analyze_requires_auth_and_csv():
    # Missing auth token
    csv_content = b"date,sales\n2024-01-01,100\n"
    files = {
        'file': ('test.csv', io.BytesIO(csv_content), 'text/csv')
    }
    response = client.post("/analyze/", files=files)
    assert response.status_code in (401, 403)


def test_forecast_requires_auth():
    response = client.post("/forecast/", json={"analysis_id": "dummy", "days": 7})
    assert response.status_code in (401, 403)

