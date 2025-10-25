from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AnalysisBase(BaseModel):
    summary: str
    key_factors: List[Dict[str, Any]]
    recommendations: List[str]
    data_points: int

class AnalysisCreate(AnalysisBase):
    user_id: str
    sales_data_id: str

class Analysis(AnalysisBase):
    id: str
    user_id: str
    sales_data_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ForecastBase(BaseModel):
    forecast_days: int
    forecast_data: Dict[str, Any]

class ForecastCreate(ForecastBase):
    analysis_id: str
    user_id: str

class Forecast(ForecastBase):
    id: str
    analysis_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ExplanationBase(BaseModel):
    feature_importance: List[Dict[str, Any]]
    shap_values: Dict[str, Any]

class ExplanationCreate(ExplanationBase):
    analysis_id: str
    user_id: str

class Explanation(ExplanationBase):
    id: str
    analysis_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

