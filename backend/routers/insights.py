from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, constr, ValidationError
from typing import List, Dict, Any, Optional
from services.supabase_client import get_supabase_client
from services.auth import verify_token

router = APIRouter()
security = HTTPBearer()

class RuleCondition(BaseModel):
    field: constr(strip_whitespace=True, min_length=1)
    op: constr(strip_whitespace=True, min_length=1) = Field(description="operator, e.g., >, <, ==, contains")
    value: Any

class InsightTemplateCreate(BaseModel):
    name: constr(strip_whitespace=True, min_length=2, max_length=64)
    rules: List[RuleCondition]
    active: bool = True

@router.post("/templates")
async def create_template(payload: InsightTemplateCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = await verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    supabase = get_supabase_client()
    ins = supabase.table('insight_templates').insert({
        'org_id': user.get('org_id'),
        'user_id': user.get('id'),
        'name': payload.name,
        'rules': [c.model_dump() for c in payload.rules],
        'active': payload.active,
    }).execute()
    if not ins.data:
        raise HTTPException(status_code=500, detail='Failed to save template')
    return { 'id': ins.data[0]['id'] }

# Simple evaluation engine
_OPS = {
    '>': lambda a, b: a is not None and b is not None and a > b,
    '<': lambda a, b: a is not None and b is not None and a < b,
    '==': lambda a, b: a == b,
    '>=': lambda a, b: a is not None and b is not None and a >= b,
    '<=': lambda a, b: a is not None and b is not None and a <= b,
    'contains': lambda a, b: (isinstance(a, str) and isinstance(b, str) and (b.lower() in a.lower()))
}

def evaluate_templates(org_id: Optional[str], record: Dict[str, Any]) -> List[str]:
    supabase = get_supabase_client()
    t = supabase.table('insight_templates').select('name,rules,active').eq('org_id', org_id).eq('active', True).execute()
    insights = []
    for tpl in (t.data or []):
        rules = tpl.get('rules') or []
        try:
            ok = True
            for cond in rules:
                field = cond.get('field')
                op = cond.get('op')
                val = cond.get('value')
                left = record.get(field)
                fn = _OPS.get(op)
                if not fn or not fn(left, val):
                    ok = False
                    break
            if ok:
                insights.append(tpl.get('name'))
        except Exception:
            continue
    return insights
