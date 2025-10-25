from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.supabase_client import get_supabase_client
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()

@router.get("/")
async def list_plugins(credentials: HTTPAuthorizationCredentials = Depends(security)):
  user = await verify_token(credentials.credentials)
  if not user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  supabase = get_supabase_client()
  org_id = user.get('org_id')
  resp = supabase.table('org_plugins').select('*').eq('org_id', org_id).execute()
  return { 'plugins': resp.data or [] }

@router.post("/toggle")
async def toggle_plugin(plugin: str, enabled: bool, credentials: HTTPAuthorizationCredentials = Depends(security)):
  user = await verify_token(credentials.credentials)
  if not user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  supabase = get_supabase_client()
  org_id = user.get('org_id')
  # upsert plugin state
  existing = supabase.table('org_plugins').select('id').eq('org_id', org_id).eq('plugin', plugin).execute()
  if existing.data:
    upd = supabase.table('org_plugins').update({ 'enabled': enabled }).eq('id', existing.data[0]['id']).execute()
    if not upd.data:
      raise HTTPException(status_code=500, detail='Failed to update plugin')
    return { 'success': True }
  ins = supabase.table('org_plugins').insert({ 'org_id': org_id, 'plugin': plugin, 'enabled': enabled }).execute()
  if not ins.data:
    raise HTTPException(status_code=500, detail='Failed to set plugin')
  return { 'success': True }
