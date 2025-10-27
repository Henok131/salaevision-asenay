from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from services.supabase_client import get_supabase_client
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()


class ConsentResponse(BaseModel):
    success: bool
    consent_given: bool


@router.post("/consent", response_model=ConsentResponse)
async def give_consent(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    supabase = get_supabase_client()
    try:
        supabase.table("users").update({"consent_given": True}).eq("id", user["id"]).execute()
    except Exception:
        pass

    return ConsentResponse(success=True, consent_given=True)
