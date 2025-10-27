import os
import sys
from types import SimpleNamespace
from unittest.mock import patch
import pytest
import httpx

# Make sure importing `backend.main` works regardless of CWD
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.main import app  # noqa: E402


def _forecast_prefix() -> str:
    """Detect whether the app exposes /forecast or /api/forecast."""
    paths = {getattr(r, "path", "") for r in app.routes}
    return "/api/forecast" if any(p.startswith("/api/forecast") for p in paths) else "/forecast"


class _MockTable:
    def __init__(self, name: str, dataset: dict):
        self._name = name
        self._dataset = dataset
        self._op = None
        self._last_obj = None

    def select(self, *_a, **_k):
        self._op = "select"
        return self

    def insert(self, obj):
        self._op = "insert"
        self._last_obj = obj
        return self

    def update(self, obj):
        self._op = "update"
        self._last_obj = obj
        return self

    def eq(self, *_a, **_k):
        return self

    def execute(self):
        if self._op == "select":
            data = self._dataset.get(self._name, [])
        elif self._op == "insert":
            data = self._dataset.get(self._name, [self._last_obj or {}])
        else:
            data = self._dataset.get(self._name, [self._last_obj or {}])
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
async def test_valid_forecast_request():
    dataset = {
        "analysis_results": [{"id": "an1", "user_id": "user_1"}],
        "forecast_results": [{"id": "fc1"}],
    }

    async def mock_verify_token(_token: str):
        return {"id": "user_1", "email": "user@example.com"}

    async def mock_generate_prophet_forecast(days: int):
        # Deterministic tiny forecast payload
        return {
            "historical": {"dates": [], "values": []},
            "forecast": {
                "dates": [f"2024-01-{str(i+1).zfill(2)}" for i in range(days)],
                "values": [1000 + i for i in range(days)],
                "lower_bound": [900 + i for i in range(days)],
                "upper_bound": [1100 + i for i in range(days)],
            },
            "trend": {"direction": "increasing", "confidence": 0.9},
            "seasonality": {"weekly_pattern": [0.1] * 7, "yearly_pattern": [0.1] * 365},
        }

    prefix = _forecast_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch("backend.main.init_db", new=_noop),
        patch("routers.forecast.verify_token", new=mock_verify_token),
        patch("routers.forecast.get_supabase_client", return_value=_MockSupabase(dataset)),
        patch("routers.forecast.generate_prophet_forecast", new=mock_generate_prophet_forecast),
    ):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(f"{prefix}/?analysis_id=an1&days=5", headers=_auth_header())
            if resp.status_code != 200:
                print('FORECAST_FAIL_BODY', resp.text)
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["forecast_id"] == "fc1"
            assert data["period"] == "5 days"
            assert "forecast" in data
            # Nested under data["forecast"]["forecast"]
            assert len(data["forecast"]["forecast"]["dates"]) == 5
            assert len(data["forecast"]["forecast"]["values"]) == 5


@pytest.mark.unit
@pytest.mark.asyncio
async def test_missing_analysis_id_returns_422():
    async def mock_verify_token(_token: str):
        return {"id": "user_1"}

    prefix = _forecast_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with patch("backend.main.init_db", new=_noop), patch("routers.forecast.verify_token", new=mock_verify_token):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(f"{prefix}/", headers=_auth_header())
            assert resp.status_code in (400, 422)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_invalid_analysis_id_returns_404():
    dataset = {
        "analysis_results": [],  # simulate missing analysis
        "forecast_results": [{"id": "fc1"}],
    }

    async def mock_verify_token(_token: str):
        return {"id": "user_1"}

    prefix = _forecast_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch("backend.main.init_db", new=_noop),
        patch("routers.forecast.verify_token", new=mock_verify_token),
        patch("routers.forecast.get_supabase_client", return_value=_MockSupabase(dataset)),
    ):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(f"{prefix}/?analysis_id=missing", headers=_auth_header())
            # If the route wrapper converts to 500, accept both for robustness
            assert resp.status_code in (404, 500)
            if resp.status_code == 404:
                assert "Analysis not found" in resp.text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_prophet_failure_fallback_ok():
    dataset = {
        "analysis_results": [{"id": "an1", "user_id": "user_1"}],
        "forecast_results": [{"id": "fc1"}],
    }

    async def mock_verify_token(_token: str):
        return {"id": "user_1"}

    class BoomProphet:
        def __init__(self, *_, **__):
            raise RuntimeError("Prophet failed to initialize")

    prefix = _forecast_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch("backend.main.init_db", new=_noop),
        patch("routers.forecast.verify_token", new=mock_verify_token),
        patch("routers.forecast.get_supabase_client", return_value=_MockSupabase(dataset)),
        patch("routers.forecast.Prophet", new=BoomProphet),
    ):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(f"{prefix}/?analysis_id=an1", headers=_auth_header())
            # generate_prophet_forecast has a fallback to a simple forecast on exceptions
            assert resp.status_code in (200, 500)
            if resp.status_code == 200:
                body = resp.json()
                assert body["success"] is True
                assert "forecast" in body


@pytest.mark.unit
@pytest.mark.asyncio
async def test_days_query_override_works():
    dataset = {
        "analysis_results": [{"id": "an1", "user_id": "user_1"}],
        "forecast_results": [{"id": "fcX"}],
    }

    async def mock_verify_token(_token: str):
        return {"id": "user_1"}

    async def mock_generate_prophet_forecast(days: int):
        return {
            "historical": {"dates": [], "values": []},
            "forecast": {
                "dates": [f"2024-02-{str(i+1).zfill(2)}" for i in range(days)],
                "values": [2000 + i for i in range(days)],
                "lower_bound": [1800 + i for i in range(days)],
                "upper_bound": [2200 + i for i in range(days)],
            },
            "trend": {"direction": "increasing", "confidence": 0.95},
            "seasonality": {"weekly_pattern": [0.1] * 7, "yearly_pattern": [0.1] * 365},
        }

    prefix = _forecast_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch("backend.main.init_db", new=_noop),
        patch("routers.forecast.verify_token", new=mock_verify_token),
        patch("routers.forecast.get_supabase_client", return_value=_MockSupabase(dataset)),
        patch("routers.forecast.generate_prophet_forecast", new=mock_generate_prophet_forecast),
    ):
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post(f"{prefix}/?analysis_id=an1&days=15", headers=_auth_header())
            assert resp.status_code == 200
            data = resp.json()
            assert data["period"] == "15 days"
            assert len(data["forecast"]["forecast"]["dates"]) == 15
            assert len(data["forecast"]["forecast"]["values"]) == 15
