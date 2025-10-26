from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import pytesseract
from PIL import Image
import io
from services.auth import verify_token
from services.supabase_client import get_supabase_client

router = APIRouter()
security = HTTPBearer()

@router.post("/")
async def ocr_image(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        # Require auth and tokens
        user = await verify_token(credentials.credentials)
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")

        content = await file.read()
        img = Image.open(io.BytesIO(content))
        # Normalize mode
        if img.mode not in ("L", "RGB"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img)

        # Token enforcement: 1 token per image (simple policy)
        supabase = get_supabase_client()
        profile = supabase.table('users').select('tokens_remaining').eq('id', user['id']).execute()
        remaining = (profile.data[0] or {}).get('tokens_remaining', 0) if profile.data else 0
        if remaining < 1:
            raise HTTPException(status_code=402, detail="Insufficient tokens. Please upgrade your plan.")

        # Deduct only on success
        supabase.table('users').update({'tokens_remaining': remaining - 1}).eq('id', user['id']).execute()
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
