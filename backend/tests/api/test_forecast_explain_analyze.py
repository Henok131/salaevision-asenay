import io
import pytest
import httpx
from fastapi import FastAPI
from routers import forecast as forecast_router
from routers import explain as explain_router
from routers import analyze as analyze_router


@pytest.mark.unit
@pytest.mark.asyncio
async def test_forecast_success(monkeypatch, supabase_factory):
    async def mock_verify(_):
        return {'id': 'user_1'}
    monkeypatch.setattr(forecast_router, 'verify_token', mock_verify)

    # Avoid heavy prophet/pandas paths by stubbing the forecast generator
    async def mock_generate(days: int):
        return {
            'historical': { 'dates': [], 'values': [] },
            'forecast': { 'dates': ['2024-01-01'], 'values': [1], 'lower_bound': [0], 'upper_bound': [2] },
            'trend': { 'direction': 'increasing', 'confidence': 0.9 },
            'seasonality': { 'weekly_pattern': [0.1]*7, 'yearly_pattern': [0.1]*365 },
        }
    monkeypatch.setattr(forecast_router, 'generate_prophet_forecast', mock_generate)

    # analysis_results select returns a row; insert into forecast_results returns id
    supabase = supabase_factory(
        select_map={'analysis_results': [{'id': 'an1', 'user_id': 'user_1'}]},
        insert_map={'forecast_results': [{'id': 'fc1'}]},
    )
    monkeypatch.setattr(forecast_router, 'get_supabase_client', lambda: supabase)

    app = FastAPI()
    app.include_router(forecast_router.router, prefix='/forecast')
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        resp = await ac.post('/forecast/?analysis_id=an1&days=7', headers={'Authorization': 'Bearer t'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['success'] is True
        assert data['period'] == '7 days'
        assert 'forecast' in data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_explain_success(monkeypatch, supabase_factory):
    async def mock_verify(_):
        return {'id': 'user_1'}
    monkeypatch.setattr(explain_router, 'verify_token', mock_verify)

    async def mock_shap():
        return {
            'feature_importance': [{'feature': 'A', 'importance': 1.0, 'impact': 'positive', 'description': 'd'}],
            'shap_values': {'sample_predictions': [], 'summary': {'total_features': 1, 'positive_features': 1, 'negative_features': 0}},
            'insights': {'key_drivers': ['A'], 'recommendations': ['Focus A'], 'risk_factors': []},
            'model_confidence': 0.87,
        }
    monkeypatch.setattr(explain_router, 'generate_shap_explanations', mock_shap)

    supabase = supabase_factory(
        select_map={'analysis_results': [{'id': 'an1', 'user_id': 'user_1'}]},
        insert_map={'explanation_results': [{'id': 'ex1'}]},
    )
    monkeypatch.setattr(explain_router, 'get_supabase_client', lambda: supabase)

    app = FastAPI()
    app.include_router(explain_router.router, prefix='/explain')
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        resp = await ac.post('/explain/?analysis_id=an1', headers={'Authorization': 'Bearer t'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['success'] is True
        assert 'explanations' in data
        assert 'feature_importance' in data['explanations']


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_success(monkeypatch, supabase_factory):
    async def mock_verify(_):
        return {'id': 'user_1'}
    monkeypatch.setattr(analyze_router, 'verify_token', mock_verify)

    # Avoid real OpenAI calls and image processing
    async def mock_text(text: str):
        return { 'tone': 'positive', 'sentiment': 'positive', 'key_themes': ['Innovation'] }
    async def mock_image(image):
        return { 'brightness': 150, 'dominant_color': '#ffffff', 'rgb_color': (255,255,255), 'dimensions': '1x1', 'aspect_ratio': 1, 'file_size': 1, 'characteristics': 'Well-lit' }
    async def mock_multi(df, text_insight, visual_insight):
        return {
            'summary': 'ok',
            'key_factors': ['f1'],
            'recommendations': ['r1'],
            'visual_insight': 'v',
            'text_insight': 't',
        }
    monkeypatch.setattr(analyze_router, 'analyze_text_sentiment', mock_text)
    monkeypatch.setattr(analyze_router, 'analyze_image_metadata', mock_image)
    monkeypatch.setattr(analyze_router, 'generate_multimodal_insights', mock_multi)

    supabase = supabase_factory(
        insert_map={'analysis_results': [{'id': 'a1'}]},
    )
    monkeypatch.setattr(analyze_router, 'get_supabase_client', lambda: supabase)

    app = FastAPI()
    app.include_router(analyze_router.router, prefix='/analyze')
    transport = httpx.ASGITransport(app=app)

    # Prepare a tiny CSV file
    csv_content = 'date,value\n2024-01-01,1\n2024-01-02,2\n'

    async with httpx.AsyncClient(transport=transport, base_url='http://test') as ac:
        files = { 'file': ('data.csv', csv_content, 'text/csv') }
        data = { 'text': 'Great launch with premium quality and fast delivery' }
        resp = await ac.post('/analyze/', files=files, data=data, headers={'Authorization': 'Bearer t'})
        print('ANALYZE_STATUS', resp.status_code)
        print('ANALYZE_BODY', resp.text[:500])
        assert resp.status_code == 200
        payload = resp.json()
        assert payload['success'] is True
        assert payload['insights']
        assert payload['data_summary']['rows'] == 2
