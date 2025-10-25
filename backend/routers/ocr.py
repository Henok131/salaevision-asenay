from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import pytesseract
from PIL import Image
import io
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()

@router.post("/")
async def ocr_image(
    file: UploadFile = File(...),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    try:
        # Optional auth: verify if provided
        if credentials:
            user = await verify_token(credentials.credentials)
            if user is None:
                raise HTTPException(status_code=401, detail="Invalid authentication")

        content = await file.read()
        img = Image.open(io.BytesIO(content))
        # Normalize mode
        if img.mode not in ("L", "RGB"):
            img = img.convert("RGB")
        text = pytesseract.image_to_string(img)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")
