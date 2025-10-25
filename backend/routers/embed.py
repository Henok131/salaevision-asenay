from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.supabase_client import get_supabase_client

router = APIRouter()

@router.get("/{public_id}")
def get_embedded_chart(public_id: str):
    supabase = get_supabase_client()
    resp = (
        supabase
        .table('dashboards')
        .select('*')
        .eq('public_id', public_id)
        .eq('is_public', True)
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    d = resp.data[0]
    # Return minimal JSON payload
    return JSONResponse(content={
        "name": d.get("name"),
        "data": d.get("data") or {},
        "public_id": d.get("public_id"),
    })
