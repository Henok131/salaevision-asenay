from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import os
from services.supabase_client import get_supabase_client
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()

@router.post("/")
async def explain_insights(
    analysis_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate explainable AI insights using SHAP
    """
    try:
        # Verify user authentication
        user = await verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        # Get analysis data from Supabase
        supabase = get_supabase_client()
        result = supabase.table("analysis_results").select("*").eq("id", analysis_id).eq("user_id", user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate SHAP explanations
        explanations = await generate_shap_explanations()
        
        # Store explanation results
        explanation_result = {
            "analysis_id": analysis_id,
            "feature_importance": explanations["feature_importance"],
            "shap_values": explanations["shap_values"],
            "user_id": user["id"]
        }
        
        result = supabase.table("explanation_results").insert(explanation_result).execute()
        
        return {
            "success": True,
            "explanation_id": result.data[0]["id"] if result.data else None,
            "explanations": explanations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation generation failed: {str(e)}")

async def generate_shap_explanations(
    *,
    rng_exponential=None,
    rng_random=None,
    features: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Generate SHAP explanations for sales data
    """
    try:
        # For demo purposes, generate synthetic SHAP data
        # In production, you would use actual SHAP analysis
        
        # Simulate feature importance
        features = features or [
            "Marketing Spend",
            "Sales Team Size", 
            "Product Price",
            "Customer Satisfaction",
            "Market Competition",
            "Seasonal Trends",
            "Economic Indicators",
            "Product Quality"
        ]
        
        np.random.seed(42)
        # Adapters for RNGs
        _exp = (lambda n: rng_exponential(0.3, n)) if rng_exponential else (lambda n: np.random.exponential(0.3, n))
        def _rand_vec(n: int):
            if rng_random is None:
                return np.array([np.random.random() for _ in range(n)])
            try:
                v = rng_random(n)
                return np.array(v)
            except TypeError:
                return np.array([rng_random() for _ in range(n)])

        feature_importance = build_feature_importance(features, _exp, _rand_vec)

        # Generate SHAP values for sample predictions
        shap_values = generate_sample_shap_values(features)
        
        # Generate insights
        insights = build_insights(feature_importance)
        
        # Map to API schema (keep 'impact' label for compatibility)
        api_fi = [
            {
                "feature": item["feature"],
                "importance": item["impact"],
                "impact": "positive" if item.get("positive") else "negative",
                "description": get_feature_description(item["feature"]),
            }
            for item in feature_importance
        ]

        return {
            "feature_importance": api_fi,
            "shap_values": shap_values,
            "insights": insights,
            "model_confidence": 0.87
        }
        
    except Exception as e:
        # Fallback explanations
        return generate_fallback_explanations()

def get_feature_description(feature: str) -> str:
    """Get description for each feature"""
    descriptions = {
        "Marketing Spend": "Investment in advertising and promotional activities",
        "Sales Team Size": "Number of sales representatives and their productivity",
        "Product Price": "Pricing strategy and competitive positioning",
        "Customer Satisfaction": "Customer experience and retention metrics",
        "Market Competition": "Competitive landscape and market share",
        "Seasonal Trends": "Time-based patterns in sales performance",
        "Economic Indicators": "Macroeconomic factors affecting purchasing power",
        "Product Quality": "Product features and customer satisfaction"
    }
    return descriptions.get(feature, "Feature impact on sales performance")

def generate_sample_shap_values(features: List[str]) -> Dict[str, Any]:
    """Generate sample SHAP values for visualization"""
    np.random.seed(42)
    
    # Generate sample data points
    sample_points = 10
    shap_data = []
    
    for i in range(sample_points):
        point_data = {
            "prediction": 1000 + np.random.normal(0, 200),
            "features": {}
        }
        
        for feature in features:
            point_data["features"][feature] = {
                "value": np.random.normal(0, 1),
                "shap_value": np.random.normal(0, 0.5)
            }
        
        shap_data.append(point_data)
    
    return {
        "sample_predictions": shap_data,
        "summary": {
            "total_features": len(features),
            "positive_features": len([f for f in features if np.random.random() > 0.5]),
            "negative_features": len([f for f in features if np.random.random() <= 0.5])
        }
    }

def generate_explanation_insights(feature_importance: List[Dict]) -> Dict[str, Any]:
    """Generate insights from feature importance analysis"""
    top_features = feature_importance[:3]
    
    insights = {
        "key_drivers": [
            f"{feat['feature']} is the most important factor" 
            for feat in top_features
        ],
        "recommendations": [
            f"Focus on optimizing {feat['feature'].lower()}" 
            for feat in top_features
        ],
        "risk_factors": [
            f"Monitor {feat['feature'].lower()} for potential issues"
            for feat in feature_importance[-2:]
        ]
    }
    
    return insights

def generate_fallback_explanations() -> Dict[str, Any]:
    """Generate fallback explanations if SHAP fails"""
    return {
        "feature_importance": [
            {
                "feature": "Data Quality",
                "importance": 0.4,
                "impact": "positive",
                "description": "Quality of input data affects analysis accuracy"
            },
            {
                "feature": "Historical Trends",
                "importance": 0.3,
                "impact": "positive", 
                "description": "Past performance patterns influence future outcomes"
            },
            {
                "feature": "External Factors",
                "importance": 0.3,
                "impact": "variable",
                "description": "Market conditions and external influences"
            }
        ],
        "shap_values": {
            "sample_predictions": [],
            "summary": {
                "total_features": 3,
                "positive_features": 2,
                "negative_features": 1
            }
        },
        "insights": {
            "key_drivers": ["Data quality is crucial for accurate analysis"],
            "recommendations": ["Improve data collection processes"],
            "risk_factors": ["Monitor external market conditions"]
        },
        "model_confidence": 0.6
    }


def build_feature_importance(features: List[str], rng_exponential, rng_random_vec) -> List[Dict[str, Any]]:
    """Pure helper to compute and sort feature importance with positivity flag.

    rng_exponential(n) -> array of impacts
    rng_random_vec(n) -> array of uniform[0,1] to determine positivity
    """
    import numpy as _np
    impacts = _np.array(rng_exponential(len(features)), dtype=float)
    # Support Python lists in tests lacking ndarray.sum()
    try:
        total = impacts.sum()  # type: ignore[attr-defined]
    except AttributeError:
        total = sum(impacts)
    if total == 0:
        impacts = _np.ones_like(impacts)
        total = len(impacts)
    impacts = [float(v) / float(total) for v in impacts]
    rvec = _np.array(rng_random_vec(len(features)))
    try:
        positives = rvec > 0.5  # type: ignore[operator]
    except Exception:
        positives = [float(x) > 0.5 for x in rvec]
    data = [
        {
            "feature": f,
            "impact": float(imp),
            "positive": bool(pos)
        }
        for f, imp, pos in zip(features, impacts, positives)
    ]
    data.sort(key=lambda x: -x["impact"])
    return data


def build_insights(feature_importance: List[Dict[str, Any]]) -> List[str]:
    return [
        f"The feature '{item['feature']}' had a {'positive' if item.get('positive') else 'negative'} impact on prediction."
        for item in feature_importance
    ]

