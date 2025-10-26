from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from services.supabase_client import get_supabase_client
from services.auth import verify_token
from datetime import datetime

router = APIRouter()
security = HTTPBearer()


class TokenStatusResponse(BaseModel):
    plan: str
    total_tokens: int
    used_tokens: int
    remaining_tokens: int
    last_used: Optional[str] = None


async def _get_or_create_token_row(user_id: str):
    supabase = get_supabase_client()
    res = supabase.table("token_usage").select("*").eq("id", user_id).execute()
    if res.data:
        return res.data[0]
    # Create with defaults
    insert = supabase.table("token_usage").insert({
        "id": user_id,
        "plan": "free",
        "total_tokens": 1000,
        "used_tokens": 0,
    }).execute()
    return insert.data[0]


@router.get("/status", response_model=TokenStatusResponse)
async def get_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    row = await _get_or_create_token_row(user["id"])
    remaining = max(0, int(row.get("total_tokens", 0)) - int(row.get("used_tokens", 0)))
    return TokenStatusResponse(
        plan=row.get("plan", "free"),
        total_tokens=int(row.get("total_tokens", 0)),
        used_tokens=int(row.get("used_tokens", 0)),
        remaining_tokens=remaining,
        last_used=row.get("last_used")
    )


class ConsumeRequest(BaseModel):
    amount: int = 1


@router.post("/consume", response_model=TokenStatusResponse)
async def consume_tokens(payload: ConsumeRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    supabase = get_supabase_client()
    row = await _get_or_create_token_row(user["id"])
    total = int(row.get("total_tokens", 0))
    used = int(row.get("used_tokens", 0))
    amount = max(1, int(payload.amount))

    if used + amount > total:
        raise HTTPException(status_code=403, detail="Token limit reached. Please upgrade your plan.")

    new_used = used + amount
    update = supabase.table("token_usage").update({
        "used_tokens": new_used,
        "last_used": datetime.utcnow().isoformat()
    }).eq("id", user["id"]).execute()

    updated = update.data[0] if update.data else {**row, "used_tokens": new_used}
    remaining = max(0, int(updated.get("total_tokens", 0)) - int(updated.get("used_tokens", 0)))
    return TokenStatusResponse(
        plan=updated.get("plan", "free"),
        total_tokens=int(updated.get("total_tokens", 0)),
        used_tokens=int(updated.get("used_tokens", 0)),
        remaining_tokens=remaining,
        last_used=updated.get("last_used")
    )
