from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.db_utils import supabase
from routes.auth import get_current_user
from utils.ratelimit import limiter, auth_key

router = APIRouter()
security = HTTPBearer()


@router.get("/history")
@limiter.limit("30/minute", key_func=auth_key)
async def usage_history(user=Depends(get_current_user), days: int = 30):
    sb = supabase()
    res = sb.table('usage_events').select('tokens_used,created_at').eq('user_id', user['id']).execute()
    from collections import defaultdict
    import datetime
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    buckets = defaultdict(int)
    for row in (res.data or []):
        try:
            ts = datetime.datetime.fromisoformat(str(row['created_at']).replace('Z','+00:00'))
            if ts >= cutoff:
                buckets[ts.strftime('%Y-%m-%d')] += int(row.get('tokens_used') or 0)
        except Exception:
            continue
    series = [{ 'date': k, 'tokens': v } for k, v in sorted(buckets.items())]
    return { 'series': series }
