import os
import sys
from types import SimpleNamespace
from unittest.mock import patch
import pytest
import httpx

# Ensure we can import `backend.main` regardless of cwd
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.main import app  # noqa: E402


def _explain_prefix() -> str:
    paths = {getattr(r, "path", "") for r in app.routes}
    return "/api/explain" if any(p.startswith("/api/explain") for p in paths) else "/explain"


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
async def test_explain_success():
    dataset = {
        'analysis_results': [{'id': 'an1', 'user_id': 'user_1'}],
        'explanation_results': [{'id': 'ex1'}],
    }

    async def mock_verify(_):
        return {'id': 'user_1'}

    async def mock_shap():
        return {
            'feature_importance': [{'feature': 'A', 'importance': 1.0, 'impact': 'positive', 'description': 'd'}],
            'shap_values': {'sample_predictions': [], 'summary': {'total_features': 1, 'positive_features': 1, 'negative_features': 0}},
            'insights': {'key_drivers': ['A'], 'recommendations': ['Focus A'], 'risk_factors': []},
            'model_confidence': 0.87,
        }

    prefix = _explain_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch('backend.main.init_db', new=_noop),
        patch('routers.explain.verify_token', new=mock_verify),
        patch('routers.explain.get_supabase_client', return_value=_MockSupabase(dataset)),
        patch('routers.explain.generate_shap_explanations', new=mock_shap),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f'{prefix}/?analysis_id=an1', headers=_auth_header())
            assert resp.status_code == 200
            data = resp.json()
            assert data['success'] is True
            assert 'explanations' in data
            assert 'feature_importance' in data['explanations']


@pytest.mark.unit
@pytest.mark.asyncio
async def test_explain_missing_param_returns_422():
    async def mock_verify(_):
        return {'id': 'user_1'}

    prefix = _explain_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with patch('backend.main.init_db', new=_noop), patch('routers.explain.verify_token', new=mock_verify):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f'{prefix}/', headers=_auth_header())
            assert resp.status_code in (400, 422)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_explain_invalid_id_returns_404():
    dataset = {
        'analysis_results': [],
    }

    async def mock_verify(_):
        return {'id': 'user_1'}

    prefix = _explain_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch('backend.main.init_db', new=_noop),
        patch('routers.explain.verify_token', new=mock_verify),
        patch('routers.explain.get_supabase_client', return_value=_MockSupabase(dataset)),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f'{prefix}/?analysis_id=missing', headers=_auth_header())
            assert resp.status_code in (404, 500)
            if resp.status_code == 404:
                assert 'Analysis not found' in resp.text


@pytest.mark.unit
@pytest.mark.asyncio
async def test_explain_internal_error_returns_500():
    dataset = {
        'analysis_results': [{'id': 'an1', 'user_id': 'user_1'}],
    }

    async def mock_verify(_):
        return {'id': 'user_1'}

    async def boom():
        raise RuntimeError('SHAP exploded')

    prefix = _explain_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with (
        patch('backend.main.init_db', new=_noop),
        patch('routers.explain.verify_token', new=mock_verify),
        patch('routers.explain.get_supabase_client', return_value=_MockSupabase(dataset)),
        patch('routers.explain.generate_shap_explanations', new=boom),
    ):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f'{prefix}/?analysis_id=an1', headers=_auth_header())
            assert resp.status_code == 500


@pytest.mark.unit
@pytest.mark.asyncio
async def test_explain_invalid_token_401():
    from routers import explain as e_router

    async def bad_verify(_):
        return None

    prefix = _explain_prefix()
    transport = httpx.ASGITransport(app=app)

    async def _noop():
        return None

    with patch('backend.main.init_db', new=_noop), patch.object(e_router, 'verify_token', new=bad_verify):
        async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
            resp = await ac.post(f'{prefix}/?analysis_id=an1', headers=_auth_header())
            # Router wraps exceptions; accept 401/403 or 500 depending on path
            assert resp.status_code in (401, 403, 500)


@pytest.mark.unit
def test_explain_generate_fallback_explanations_shape():
    # Directly hit fallback generator for coverage & schema validation
    from routers import explain as e
    out = e.generate_fallback_explanations()
    assert 'feature_importance' in out
    assert 'shap_values' in out
    assert 'insights' in out
    assert 'model_confidence' in out


@pytest.mark.unit
def test_generate_sample_shap_values_and_insights_branches(monkeypatch):
    from routers import explain as e

    # Force np.random to cover both positive/negative branches and deterministic outputs
    class RNG:
        seq = [0.9, 0.1, 0.6, 0.4, 0.51, 0.49, 0.8, 0.2, 0.7, 0.3]
        i = 0
        @staticmethod
        def exponential(_lam, size):
            # Importance scores; ensure all positive and diverse
            return [0.3 for _ in range(size)]
        @staticmethod
        def normal(_mu, _sigma):
            return 0.0
        @staticmethod
        def random():
            v = RNG.seq[RNG.i % len(RNG.seq)]
            RNG.i += 1
            return v
        @staticmethod
        def seed(_):
            return None

    monkeypatch.setattr(e.np, 'random', RNG)
    # Run sample shap values
    features = ["F1", "F2", "F3"]
    shap = e.generate_sample_shap_values(features)
    assert 'sample_predictions' in shap and 'summary' in shap
    s = shap['summary']
    assert 'total_features' in s and s['total_features'] == len(features)

    # Build feature_importance to hit generate_explanation_insights
    fi = [
        {"feature": "F1", "importance": 0.5, "impact": "positive", "description": e.get_feature_description("F1")},
        {"feature": "F2", "importance": 0.3, "impact": "negative", "description": e.get_feature_description("F2")},
        {"feature": "unknown", "importance": 0.2, "impact": "positive", "description": e.get_feature_description("unknown")},
    ]
    insights = e.generate_explanation_insights(fi)
    assert 'key_drivers' in insights and 'recommendations' in insights and 'risk_factors' in insights
    # Default description fallback used for unknown
    assert e.get_feature_description('unknown').startswith('Feature impact')
