from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from routes.auth import get_current_user
from utils.db_utils import supabase
import os

router = APIRouter()

MODE = os.getenv('RECOMMENDATION_MODE', 'ai')

@router.get('/recommendation/{lead_id}')
async def recommendation(lead_id: str, user = Depends(get_current_user)):
    sb = supabase()
    lead = sb.table('leads').select('*').eq('id', lead_id).limit(1).execute()
    if not lead.data:
        raise HTTPException(status_code=404, detail='Lead not found')
    row = lead.data[0]
    last = row.get('last_contacted_at')
    last_dt = None
    try:
        last_dt = datetime.fromisoformat(str(last).replace('Z','+00:00')) if last else None
    except Exception:
        pass
    rec = None
    # Fallback rule-based recommendation
    if (row.get('score') or 0) >= 80 and (not last_dt or (datetime.utcnow() - last_dt) > timedelta(days=3)):
        rec = 'Call this lead. Score is high.'
    else:
        rec = 'Nurture via email.'
    return { 'recommendation': rec }
