from fastapi import APIRouter, Request, HTTPException
import os
import logging

router = APIRouter()

@router.post('/webhook/event')
async def receive_event(request: Request):
    token = request.headers.get('x-webhook-token') or request.query_params.get('token')
    expected = os.getenv('WEBHOOK_TOKEN')
    if not expected or token != expected:
        raise HTTPException(status_code=401, detail='Invalid webhook token')
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    logging.info('[WEBHOOK] event: %s', payload)
    return { 'status': 'ok' }
