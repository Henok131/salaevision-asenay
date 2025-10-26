from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.supabase_client import get_supabase_client
from services.auth import verify_token
import uuid
from backend.models.pydantic_schemas import TogglePublicRequest

router = APIRouter()
security = HTTPBearer()


def generate_public_id() -> str:
    return uuid.uuid4().hex[:10]


@router.post("/toggle_public")
async def toggle_public(payload: TogglePublicRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    supabase = get_supabase_client()
    # Enforce org policy: allow_public_embeds must be true
    org = supabase.table("orgs").select("allow_public_embeds").eq("id", user.get("org_id")).execute()
    allow_embeds = True if not org.data else bool(org.data[0].get("allow_public_embeds", True))
    if payload.is_public and not allow_embeds:
        raise HTTPException(status_code=403, detail="Public embeds are disabled for this org")

    # Enforce RBAC: only admin/analyst can toggle
    me = supabase.table("users").select("role").eq("id", user["id"]).execute()
    if not me.data or me.data[0].get("role") not in ("admin", "analyst"):
        raise HTTPException(status_code=403, detail="Only admin or analyst can toggle public status")

    # Toggle specific dashboard if provided, else latest
    if payload.dashboard_id:
        dash = supabase.table("dashboards").select("id,public_id,is_public").eq("id", payload.dashboard_id).eq("user_id", user["id"]).limit(1).execute()
    else:
        dash = supabase.table("dashboards").select("id,public_id,is_public").eq("user_id", user["id"]).order("created_at", desc=True).limit(1).execute()
    if not dash.data:
        # create a placeholder dashboard if none exists
        new_public_id = generate_public_id() if payload.is_public else None
        ins = supabase.table("dashboards").insert({
            "user_id": user["id"],
            "org_id": user.get("org_id"),
            "name": "Default Dashboard",
            "data": {},
            "public_id": new_public_id,
            "is_public": payload.is_public,
        }).execute()
        if not ins.data:
            raise HTTPException(status_code=500, detail="Failed to create dashboard")
        d = ins.data[0]
        return {"id": d["id"], "is_public": d["is_public"], "public_id": d.get("public_id")}

    d = dash.data[0]
    new_public_id = d.get("public_id") or (generate_public_id() if payload.is_public else None)
    upd = supabase.table("dashboards").update({
        "is_public": payload.is_public,
        "public_id": new_public_id,
    }).eq("id", d["id"]).execute()
    if not upd.data:
        raise HTTPException(status_code=500, detail="Failed to update dashboard")
    d2 = upd.data[0]
    return {"id": d2["id"], "is_public": d2["is_public"], "public_id": d2.get("public_id")}
