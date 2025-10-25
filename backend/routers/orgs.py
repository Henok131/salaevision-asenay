from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import uuid
from services.supabase_client import get_supabase_client
from services.auth import verify_token
import uuid as _uuid

router = APIRouter()
security = HTTPBearer()

@router.post("/create")
async def create_org(name: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase = get_supabase_client()
    # Create org
    org = supabase.table("orgs").insert({"name": name}).execute()
    if not org.data:
        raise HTTPException(status_code=500, detail="Failed to create org")
    org_id = org.data[0]["id"]
    # Attach current user as admin
    supabase.table("users").update({"org_id": org_id, "role": "admin"}).eq("id", user["id"]).execute()
    return {"org_id": org_id, "name": name}

@router.post("/invite")
async def invite_user_to_org(email: str, role: str, org_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if role not in ("admin", "analyst", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")
    supabase = get_supabase_client()
    token = str(_uuid.uuid4())
    inv = supabase.table("org_invitations").insert({"org_id": org_id, "email": email, "role": role, "token": token}).execute()
    if not inv.data:
        raise HTTPException(status_code=500, detail="Failed to create invitation")
    # TODO: send email with token link
    return {"success": True, "token": token}

@router.get("/members")
async def get_org_members(org_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase = get_supabase_client()
    members = supabase.table("users").select("id,email,role,created_at").eq("org_id", org_id).execute()
    return {"members": members.data or []}

@router.get("/me")
async def get_user_org(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase = get_supabase_client()
    org = None
    if user.get("org_id"):
        o = supabase.table("orgs").select("id,name,domain").eq("id", user["org_id"]).execute()
        org = o.data[0] if o.data else None
    return {"user": user, "org": org}

@router.post("/assign_role")
async def assign_role(user_id: str, role: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    current = await verify_token(credentials.credentials)
    if not current:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if role not in ("admin", "analyst", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")
    supabase = get_supabase_client()
    # Ensure current user is admin in the same org
    cur = supabase.table("users").select("org_id,role").eq("id", current["id"]).execute()
    if not cur.data:
        raise HTTPException(status_code=403, detail="Forbidden")
    if cur.data[0].get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    org_id = cur.data[0].get("org_id")
    upd = supabase.table("users").update({"role": role}).eq("id", user_id).eq("org_id", org_id).execute()
    if not upd.data:
        raise HTTPException(status_code=500, detail="Failed to update role")
    return {"success": True}
