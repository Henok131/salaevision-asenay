from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import pandas as pd
import os
import io
from typing import Dict, Any, Optional
import json
from PIL import Image, ImageStat
from openai import OpenAI
from services.supabase_client import get_supabase_client
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()

# Initialize OpenAI (v1 client)
_openai_client = OpenAI()

@router.post("/")
async def analyze_sales_data(
    file: UploadFile = File(...),
    image: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze uploaded sales data and return AI-generated insights
    """
    try:
        # Verify user authentication
        user = await verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        
        # Check file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read CSV data
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Basic data validation
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")
        
        # Token usage (1 token = 100 words)
        tokens_used = 0
        if text:
            # Approximate word count
            words = len(text.split())
            tokens_used = max(tokens_used, (words + 99) // 100)

        # Validate token availability for user (from users table)
        supabase = get_supabase_client()
        user_row = supabase.table("users").select("id,tokens_remaining,plan").eq("id", user["id"]).execute()
        if not user_row.data:
            raise HTTPException(status_code=403, detail="User profile not found")
        remaining = (user_row.data[0] or {}).get("tokens_remaining", 0)
        if tokens_used > 0 and remaining < tokens_used:
            raise HTTPException(status_code=402, detail="Insufficient tokens. Please upgrade your plan.")

        # Process multimodal inputs
        text_insight = None
        visual_insight = None
        
        if text:
            text_insight = await analyze_text_sentiment(text)
        
        if image:
            visual_insight = await analyze_image_metadata(image)
        
        # Generate AI insights using OpenAI with multimodal context
        insights = await generate_multimodal_insights(df, text_insight, visual_insight)
        
        # Store analysis results in Supabase
        analysis_result = {
            "user_id": user["id"],
            "filename": file.filename,
            "summary": insights["summary"],
            "key_factors": insights["key_factors"],
            "recommendations": insights["recommendations"],
            "data_points": len(df),
            "text_insight": text_insight,
            "visual_insight": visual_insight
        }
        
        result = supabase.table("analysis_results").insert(analysis_result).execute()

        # Deduct tokens_used
        if tokens_used > 0:
            new_remaining = max(0, int(remaining) - int(tokens_used))
            supabase.table("users").update({"tokens_remaining": new_remaining}).eq("id", user["id"]).execute()
        
        return {
            "success": True,
            "analysis_id": result.data[0]["id"] if result.data else None,
            "insights": insights,
            "text_insight": text_insight,
            "visual_insight": visual_insight,
            "data_summary": {
                "rows": len(df),
                "columns": list(df.columns),
                "date_range": get_date_range(df) if 'date' in df.columns else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

async def analyze_text_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze text sentiment and tone using OpenAI
    """
    try:
        response = _openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a marketing sentiment analyst. Analyze the tone, sentiment, and key themes of marketing text."},
                {"role": "user", "content": f"Analyze the tone and sentiment of this marketing text: {text}"}
            ],
            max_tokens=200,
            temperature=0.7,
        )

        analysis = response.choices[0].message.content
        
        return {
            "tone": analysis,
            "sentiment": "positive" if any(word in analysis.lower() for word in ["positive", "optimistic", "confident", "exciting"]) else "neutral",
            "key_themes": extract_themes(text)
        }
        
    except Exception as e:
        return {
            "tone": "Unable to analyze tone",
            "sentiment": "neutral",
            "key_themes": []
        }

async def analyze_image_metadata(image: UploadFile) -> Dict[str, Any]:
    """
    Extract image metadata: brightness, dominant color, file size
    """
    try:
        # Read image data
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Calculate brightness
        stat = ImageStat.Stat(img)
        brightness = sum(stat.mean) / len(stat.mean)
        
        # Get dominant color (resize to 1x1 and get pixel)
        dominant_color = img.resize((1, 1)).getpixel((0, 0))
        
        # Convert RGB to hex
        hex_color = f"#{dominant_color[0]:02x}{dominant_color[1]:02x}{dominant_color[2]:02x}"
        
        # Get image characteristics
        width, height = img.size
        aspect_ratio = width / height if height > 0 else 1
        
        return {
            "brightness": round(brightness, 2),
            "dominant_color": hex_color,
            "rgb_color": dominant_color,
            "dimensions": f"{width}x{height}",
            "aspect_ratio": round(aspect_ratio, 2),
            "file_size": len(image_data),
            "characteristics": get_image_characteristics(brightness, dominant_color, aspect_ratio)
        }
        
    except Exception as e:
        return {
            "brightness": 0,
            "dominant_color": "#000000",
            "rgb_color": (0, 0, 0),
            "dimensions": "0x0",
            "aspect_ratio": 1,
            "file_size": 0,
            "characteristics": "Unable to analyze image"
        }

async def generate_multimodal_insights(df: pd.DataFrame, text_insight: Optional[Dict], visual_insight: Optional[Dict]) -> Dict[str, Any]:
    """
    Generate AI insights from sales data with multimodal context
    """
    try:
        # Prepare data summary for AI
        data_summary = {
            "shape": df.shape,
            "columns": list(df.columns),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "date_columns": df.select_dtypes(include=['datetime']).columns.tolist(),
            "sample_data": df.head().to_dict()
        }
        
        # Build multimodal context
        context_parts = []
        
        # Sales data context
        context_parts.append(f"Sales Data: {data_summary['shape'][0]} rows, {data_summary['shape'][1]} columns")
        
        # Text context
        if text_insight:
            context_parts.append(f"Marketing Text Tone: {text_insight.get('tone', 'N/A')}")
            context_parts.append(f"Sentiment: {text_insight.get('sentiment', 'neutral')}")
        
        # Visual context
        if visual_insight:
            context_parts.append(f"Image Characteristics: {visual_insight.get('characteristics', 'N/A')}")
            context_parts.append(f"Dominant Color: {visual_insight.get('dominant_color', '#000000')}")
            context_parts.append(f"Brightness: {visual_insight.get('brightness', 0)}")
        
        # Create comprehensive prompt
        prompt = f"""
        Analyze this multimodal sales data and provide integrated insights:
        
        Sales Data Summary:
        - Shape: {data_summary['shape']}
        - Columns: {data_summary['columns']}
        - Numeric columns: {data_summary['numeric_columns']}
        - Sample data: {json.dumps(data_summary['sample_data'], default=str)}
        
        Additional Context:
        {chr(10).join(context_parts) if context_parts else "No additional context provided"}
        
        Please provide:
        1. A comprehensive summary integrating sales data, text tone, and visual elements
        2. Key factors affecting sales performance (data-driven and creative)
        3. Actionable recommendations that consider both quantitative and qualitative insights
        4. Visual and textual insights that complement the sales analysis
        
        Format your response as JSON with keys: summary, key_factors, recommendations, visual_insight, text_insight
        """
        
        response = _openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a multimodal sales analytics expert. Analyze sales data, marketing text, and visual elements to provide integrated, explainable insights."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.7,
        )

        # Parse AI response
        ai_response = response.choices[0].message.content
        
        try:
            insights = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            insights = {
                "summary": ai_response,
                "key_factors": ["Multimodal analysis completed"],
                "recommendations": ["Review the generated summary for insights"],
                "visual_insight": "Visual analysis integrated into main insights",
                "text_insight": "Text analysis integrated into main insights"
            }
        
        return insights
        
    except Exception as e:
        # Fallback analysis if OpenAI fails
        return {
            "summary": f"Analyzed {len(df)} rows of sales data with multimodal context",
            "key_factors": ["Data volume", "Multimodal integration", "Context richness"],
            "recommendations": ["Consider data quality improvements", "Enhance multimodal inputs"],
            "visual_insight": "Visual analysis not available",
            "text_insight": "Text analysis not available"
        }

def extract_themes(text: str) -> list:
    """Extract key themes from text"""
    # Simple keyword extraction (in production, use more sophisticated NLP)
    themes = []
    if any(word in text.lower() for word in ["sale", "discount", "offer", "deal"]):
        themes.append("Promotional")
    if any(word in text.lower() for word in ["new", "launch", "introduce", "innovative"]):
        themes.append("Innovation")
    if any(word in text.lower() for word in ["quality", "premium", "luxury", "exclusive"]):
        themes.append("Quality")
    if any(word in text.lower() for word in ["fast", "quick", "instant", "immediate"]):
        themes.append("Urgency")
    return themes if themes else ["General"]

def get_image_characteristics(brightness: float, dominant_color: tuple, aspect_ratio: float) -> str:
    """Get human-readable image characteristics"""
    characteristics = []
    
    # Brightness analysis
    if brightness > 200:
        characteristics.append("Bright and vibrant")
    elif brightness > 150:
        characteristics.append("Well-lit")
    elif brightness > 100:
        characteristics.append("Moderately lit")
    else:
        characteristics.append("Dark or muted")
    
    # Color analysis
    r, g, b = dominant_color
    if r > g and r > b:
        characteristics.append("Red-dominant")
    elif g > r and g > b:
        characteristics.append("Green-dominant")
    elif b > r and b > g:
        characteristics.append("Blue-dominant")
    else:
        characteristics.append("Balanced colors")
    
    # Aspect ratio analysis
    if aspect_ratio > 1.5:
        characteristics.append("Wide format")
    elif aspect_ratio < 0.7:
        characteristics.append("Tall format")
    else:
        characteristics.append("Square format")
    
    return ", ".join(characteristics)

def get_date_range(df: pd.DataFrame) -> Dict[str, str]:
    """Extract date range from dataframe"""
    try:
        date_col = df['date'] if 'date' in df.columns else df.columns[0]
        return {
            "start": str(df[date_col].min()),
            "end": str(df[date_col].max())
        }
    except:
        return None


@router.get("/history/")
async def get_analysis_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = 20,
):
    """Return recent analysis results for the authenticated user."""
    try:
        user = await verify_token(credentials.credentials)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication")

        supabase = get_supabase_client()
        result = (
            supabase
            .table("analysis_results")
            .select("*")
            .eq("user_id", user["id"])
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        return {"results": result.data or []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")
