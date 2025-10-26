from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth import verify_token
from services.supabase_client import get_supabase_client
from services.ratelimit import limiter, auth_key

router = APIRouter()
security = HTTPBearer()

@router.get("/history")
@limiter.limit("30/minute", key_func=auth_key)
async def usage_history(credentials: HTTPAuthorizationCredentials = Depends(security), days: int = 30):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase = get_supabase_client()
    # Aggregate tokens per day for the current user
    # Note: Supabase RPC would be more efficient; simple client-side aggregate here
    res = supabase.table('usage_events').select('tokens_used,created_at').eq('user_id', user['id']).execute()
    data = res.data or []
    # naive aggregation (client-side)
    from collections import defaultdict
    import datetime
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    buckets = defaultdict(int)
    for row in data:
        try:
            ts = datetime.datetime.fromisoformat(str(row['created_at']).replace('Z','+00:00'))
            if ts >= cutoff:
                day = ts.strftime('%Y-%m-%d')
                buckets[day] += int(row.get('tokens_used') or 0)
        except Exception:
            continue
    # Return sorted series
    series = [{ 'date': k, 'tokens': v } for k, v in sorted(buckets.items())]
    return { 'series': series }
