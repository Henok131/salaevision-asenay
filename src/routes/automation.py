import os
from fastapi import APIRouter, Depends, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from utils.db_utils import supabase
from routes.auth import get_current_user, require_role

router = APIRouter()

REMINDER_DAYS = int(os.getenv('REMINDER_DAYS', '7'))

scheduler: AsyncIOScheduler | None = None


def ensure_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
        scheduler.start()
        scheduler.add_job(run_reminders, 'interval', hours=24, next_run_time=datetime.utcnow())


async def run_reminders():
    sb = supabase()
    cutoff = datetime.utcnow() - timedelta(days=REMINDER_DAYS)
    q = sb.table('leads').select('*').eq('reminder_enabled', True).eq('reminder_sent', False).execute()
    for lead in q.data or []:
        last = lead.get('last_contacted_at')
        try:
            last_dt = datetime.fromisoformat(str(last).replace('Z','+00:00')) if last else None
        except Exception:
            last_dt = None
        if last_dt and last_dt > cutoff:
            continue
        # Mark reminder_sent; actual email can be sent through email route or here if desired
        sb.table('leads').update({'reminder_sent': True}).eq('id', lead['id']).execute()


@router.post('/reminder/toggle')
async def toggle_reminder(lead_id: str, enabled: bool, user=Depends(get_current_user)):
    sb = supabase()
    upd = sb.table('leads').update({'reminder_enabled': enabled}).eq('id', lead_id).execute()
    if not upd.data:
        raise HTTPException(status_code=404, detail='Lead not found')
    return { 'lead_id': lead_id, 'reminder_enabled': enabled }
