import os
from supabase import create_client, Client
from typing import Any, Dict, Optional

_SUPABASE: Optional[Client] = None


def supabase() -> Client:
    global _SUPABASE
    if _SUPABASE is None:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_ANON_KEY')
        if not url or not key:
            raise RuntimeError('Missing Supabase env (SUPABASE_URL, SUPABASE_*_KEY)')
        _SUPABASE = create_client(url, key)
    return _SUPABASE


def insert_usage_event(user_id: str, org_id: Optional[str], tokens_used: int, event_type: str) -> None:
    sb = supabase()
    sb.table('usage_events').insert({
        'user_id': user_id,
        'org_id': org_id,
        'tokens_used': tokens_used,
        'event_type': event_type,
    }).execute()
