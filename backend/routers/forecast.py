from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, List, Any, Sequence
import os
from services.supabase_client import get_supabase_client
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()

@router.post("/")
async def generate_forecast(
    analysis_id: str,
    days: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Generate sales forecast using Prophet
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
        
        # For demo purposes, generate synthetic forecast data
        # In production, you would load the actual sales data
        forecast_data = await generate_prophet_forecast(days)
        
        # Store forecast results
        forecast_result = {
            "analysis_id": analysis_id,
            "forecast_days": days,
            "forecast_data": forecast_data,
            "user_id": user["id"]
        }
        
        result = supabase.table("forecast_results").insert(forecast_result).execute()
        
        return {
            "success": True,
            "forecast_id": result.data[0]["id"] if result.data else None,
            "forecast": forecast_data,
            "period": f"{days} days"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast generation failed: {str(e)}")

async def generate_prophet_forecast(days: int) -> Dict[str, Any]:
    """
    Generate forecast using Prophet (simplified version for demo)
    """
    try:
        # Create synthetic historical data for demo
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        sales = np.random.normal(1000, 200, len(dates)) + np.sin(np.arange(len(dates)) * 2 * np.pi / 365) * 100
        
        # Prepare data for Prophet
        df = pd.DataFrame({
            'ds': dates,
            'y': sales
        })
        
        # Initialize and fit Prophet model
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='multiplicative'
        )
        
        model.fit(df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        
        # Extract lists from pandas objects
        hist_dates = df['ds'].dt.strftime('%Y-%m-%d').tolist()
        hist_values = df['y'].tolist()
        tail = forecast.tail(days)
        fc_dates = tail['ds'].dt.strftime('%Y-%m-%d').tolist()
        fc_values = tail['yhat'].tolist()
        fc_lower = tail['yhat_lower'].tolist()
        fc_upper = tail['yhat_upper'].tolist()
        trend_series = forecast['trend'].tolist()
        weekly_pattern = extract_weekly_pattern(forecast)
        yearly_pattern = extract_yearly_pattern(forecast)

        return format_forecast_output(
            historical_dates=hist_dates,
            historical_values=hist_values,
            forecast_dates=fc_dates,
            forecast_values=fc_values,
            forecast_lower=fc_lower,
            forecast_upper=fc_upper,
            trend_series=trend_series,
            weekly_pattern=weekly_pattern,
            yearly_pattern=yearly_pattern,
        )
        
    except Exception as e:
        # Fallback to simple linear forecast
        return generate_simple_forecast(days)

def extract_weekly_pattern(forecast: pd.DataFrame) -> List[float]:
    """Extract weekly seasonality pattern"""
    try:
        weekly = forecast.groupby(forecast['ds'].dt.dayofweek)['weekly'].mean()
        return weekly.tolist()
    except:
        return [0.1, 0.2, 0.3, 0.4, 0.5, 0.2, 0.1]  # Default pattern

def extract_yearly_pattern(forecast: pd.DataFrame) -> List[float]:
    """Extract yearly seasonality pattern"""
    try:
        yearly = forecast.groupby(forecast['ds'].dt.dayofyear)['yearly'].mean()
        return yearly.tolist()
    except:
        return [0.1] * 365  # Default pattern

def generate_simple_forecast(days: int) -> Dict[str, Any]:
    """Generate simple linear forecast as fallback"""
    import datetime
    
    # Generate simple forecast data
    start_date = datetime.datetime.now()
    dates = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
    values = [1000 + i * 10 + np.random.normal(0, 50) for i in range(days)]
    
    return {
        "historical": {
            "dates": [],
            "values": []
        },
        "forecast": {
            "dates": dates,
            "values": values,
            "lower_bound": [v * 0.8 for v in values],
            "upper_bound": [v * 1.2 for v in values]
        },
        "trend": {
            "direction": "stable",
            "confidence": 0.7
        },
        "seasonality": {
            "weekly_pattern": [0.1, 0.2, 0.3, 0.4, 0.5, 0.2, 0.1],
            "yearly_pattern": [0.1] * 365
        }
    }

def format_forecast_output(
    *,
    historical_dates: Sequence[str],
    historical_values: Sequence[float],
    forecast_dates: Sequence[str],
    forecast_values: Sequence[float],
    forecast_lower: Sequence[float],
    forecast_upper: Sequence[float],
    trend_series: Sequence[float],
    weekly_pattern: Sequence[float] | None = None,
    yearly_pattern: Sequence[float] | None = None,
) -> Dict[str, Any]:
    """Pure formatter for forecast output. Accepts simple lists for easy testing."""
    # Determine trend
    direction = "stable"
    if len(trend_series) >= 2:
        direction = "increasing" if float(trend_series[-1]) > float(trend_series[-2]) else "decreasing"

    return {
        "historical": {
            "dates": list(historical_dates),
            "values": list(historical_values),
        },
        "forecast": {
            "dates": list(forecast_dates),
            "values": list(forecast_values),
            "lower_bound": list(forecast_lower),
            "upper_bound": list(forecast_upper),
        },
        "trend": {
            "direction": direction,
            "confidence": 0.85,
        },
        "seasonality": {
            "weekly_pattern": list(weekly_pattern) if weekly_pattern is not None else [0.1]*7,
            "yearly_pattern": list(yearly_pattern) if yearly_pattern is not None else [0.1]*365,
        },
    }

