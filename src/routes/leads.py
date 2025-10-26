import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from utils.db_utils import supabase, insert_usage_event
from utils.openai_utils import score_lead
from routes.auth import get_current_user, require_role
from utils.ratelimit import limiter, auth_key

router = APIRouter()

RATE_LIMIT_ANALYZE = int(os.getenv('RATE_LIMIT_ANALYZE', '10'))
TOKEN_COST_PER_TEXT = int(os.getenv('TOKEN_COST_PER_TEXT', '1'))


class LeadCreate(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None


@router.post("/")
async def create_lead(payload: LeadCreate, user=Depends(get_current_user)):
    sb = supabase()
    row = {
        'name': payload.name,
        'email': payload.email,
        'company': payload.company,
        'title': payload.title,
        'source': payload.source,
    }
    res = sb.table('leads').insert(row).execute()
    if not res.data:
        raise HTTPException(status_code=500, detail='Failed to create lead')
    return {"id": res.data[0]['id']}


@router.get("/")
async def list_leads(user=Depends(get_current_user)):
    sb = supabase()
    res = sb.table('leads').select('*').order('created_at', desc=True).limit(100).execute()
    return {"leads": res.data or []}


class ScoreRequest(BaseModel):
    lead_id: Optional[str] = None
    lead: Optional[dict] = None


@router.post("/score")
@limiter.limit("{}/minute".format(RATE_LIMIT_ANALYZE), key_func=auth_key)
async def score_route(payload: ScoreRequest, user=Depends(get_current_user)):
    sb = supabase()
    lead_data = payload.lead
    if payload.lead_id:
        q = sb.table('leads').select('*').eq('id', payload.lead_id).limit(1).execute()
        if not q.data:
            raise HTTPException(status_code=404, detail='Lead not found')
        lead_data = q.data[0]
    if not lead_data:
        raise HTTPException(status_code=400, detail='Missing lead data')

    # Token enforcement (simple per-call text token)
    prof = sb.table('users').select('tokens_remaining').eq('id', user['id']).execute()
    remaining = (prof.data[0] or {}).get('tokens_remaining', 0) if prof.data else 0
    if remaining < TOKEN_COST_PER_TEXT:
        raise HTTPException(status_code=402, detail='Insufficient tokens')

    result = score_lead(lead_data)
    score = int(result.get('score', 5))
    reason = result.get('reason', 'n/a')
    if payload.lead_id:
        sb.table('leads').update({'score': score, 'reason': reason}).eq('id', payload.lead_id).execute()

    # Deduct on success and record usage
    sb.table('users').update({'tokens_remaining': remaining - TOKEN_COST_PER_TEXT}).eq('id', user['id']).execute()
    insert_usage_event(user['id'], user.get('org_id'), TOKEN_COST_PER_TEXT, 'score')

    return {"score": score, "reason": reason}
