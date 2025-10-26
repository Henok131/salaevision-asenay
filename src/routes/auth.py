from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict
from utils.db_utils import supabase

router = APIRouter()
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    try:
        token = credentials.credentials
        sb = supabase()
        resp = sb.auth.get_user(token)
        if not getattr(resp, 'user', None):
            raise HTTPException(status_code=401, detail='Invalid token')
        user = resp.user
        # Fetch role/org from users table
        profile = sb.table('users').select('*').eq('id', user.id).execute()
        if profile.data:
            row = profile.data[0]
            return {"id": row.get('id'), "email": row.get('email'), "role": row.get('role', 'viewer'), "org_id": row.get('org_id')}
        return {"id": user.id, "email": user.email, "role": 'viewer', "org_id": None}
    except Exception:
        raise HTTPException(status_code=401, detail='Unauthorized')


def require_role(roles):
    def checker(user = Depends(get_current_user)):
        if user.get('role') not in roles:
            raise HTTPException(status_code=403, detail='Forbidden')
        return user
    return checker
