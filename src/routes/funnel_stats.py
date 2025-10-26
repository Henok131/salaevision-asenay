from fastapi import APIRouter, Depends
from routes.auth import get_current_user
from utils.db_utils import supabase

router = APIRouter()

@router.get('/funnel-stats')
async def funnel_stats(user = Depends(get_current_user)):
    sb = supabase()
    # Total leads
    total = sb.table('leads').select('id', count='exact').execute()
    total_leads = total.count or 0
    # Leads contacted (any contact row)
    contacted = sb.table('contacts').select('id', count='exact').execute()
    leads_contacted = contacted.count or 0
    # Leads scored (score not null)
    scored = sb.table('leads').select('id', count='exact').not_.is_('score', None).execute()
    leads_scored = scored.count or 0
    # Conversions by week (proxy via contacts count grouped by week)
    # Supabase Python SDK lacks direct group-by; fetch recent and aggregate client-side
    conv = sb.table('contacts').select('id,sent_at').order('sent_at', desc=True).limit(1000).execute()
    from collections import defaultdict
    import datetime
    weekly = defaultdict(int)
    for row in conv.data or []:
        ts = row.get('sent_at')
        try:
            dt = datetime.datetime.fromisoformat(str(ts).replace('Z','+00:00'))
            year, week, _ = dt.isocalendar()
            weekly[f"{year}-W{week}"] += 1
        except Exception:
            continue
    return {
        'total_leads': total_leads,
        'leads_contacted': leads_contacted,
        'leads_scored': leads_scored,
        'conversions_by_week': weekly,
    }
