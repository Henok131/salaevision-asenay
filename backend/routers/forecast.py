from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import numpy as np
from prophet import Prophet
from typing import Dict, List, Any
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
        
        # Extract forecast data
        forecast_data = {
            "historical": {
                "dates": df['ds'].dt.strftime('%Y-%m-%d').tolist(),
                "values": df['y'].tolist()
            },
            "forecast": {
                "dates": forecast.tail(days)['ds'].dt.strftime('%Y-%m-%d').tolist(),
                "values": forecast.tail(days)['yhat'].tolist(),
                "lower_bound": forecast.tail(days)['yhat_lower'].tolist(),
                "upper_bound": forecast.tail(days)['yhat_upper'].tolist()
            },
            "trend": {
                "direction": "increasing" if forecast['trend'].iloc[-1] > forecast['trend'].iloc[-2] else "decreasing",
                "confidence": 0.85
            },
            "seasonality": {
                "weekly_pattern": extract_weekly_pattern(forecast),
                "yearly_pattern": extract_yearly_pattern(forecast)
            }
        }
        
        return forecast_data
        
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

