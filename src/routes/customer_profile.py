from fastapi import APIRouter, Depends, HTTPException
from routes.auth import get_current_user
from utils.db_utils import supabase

router = APIRouter()

@router.get("/customer_profile/{lead_id}")
async def customer_profile(lead_id: str, user=Depends(get_current_user)):
    sb = supabase()
    # Lead info
    lead = sb.table('leads').select('*').eq('id', lead_id).limit(1).execute()
    if not lead.data:
        raise HTTPException(status_code=404, detail='Lead not found')
    # Timeline: contacts/emails + score events (reason in leads table and contacts messages)
    contacts = sb.table('contacts').select('*').eq('lead_id', lead_id).order('sent_at', desc=True).limit(100).execute()
    # Usage: per-user bounded (could be org-bound in future)
    usage = sb.table('usage_events').select('tokens_used,created_at').eq('user_id', user['id']).order('created_at', desc=True).limit(100).execute()
    # Score history: if you track scoring events separately, query; else derive from contacts/messages
    # For demo, we return latest score + reason
    profile = {
        'lead': lead.data[0],
        'timeline': contacts.data or [],
        'usage': usage.data or [],
        'score': lead.data[0].get('score'),
        'reason': lead.data[0].get('reason')
    }
    return profile
