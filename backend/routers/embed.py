from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.supabase_client import get_supabase_client
from services.ratelimit import limiter, get_remote_address

router = APIRouter()

@router.get("/{public_id}")
@limiter.limit("20/minute")
def get_embedded_chart(public_id: str):
    supabase = get_supabase_client()
    resp = (
        supabase
        .table('dashboards')
        .select('id,name,data,public_id,is_public,org_id')
        .eq('public_id', public_id)
        .eq('is_public', True)
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    d = resp.data[0]
    # Re-check org embed policy at read-time
    org = supabase.table('orgs').select('allow_public_embeds').eq('id', d.get('org_id')).execute()
    allow_embeds = True if not org.data else bool(org.data[0].get('allow_public_embeds', True))
    if not allow_embeds:
        raise HTTPException(status_code=403, detail="Public embeds are disabled for this org")
    # Return minimal JSON payload
    return JSONResponse(content={
        "name": d.get("name"),
        "data": d.get("data") or {},
        "public_id": d.get("public_id"),
    })
