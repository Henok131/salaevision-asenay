from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from routes.auth import get_current_user
from utils.db_utils import supabase
from utils.embeddings import get_embedding

router = APIRouter()

class SearchPayload(BaseModel):
    query: str

class SearchResult(BaseModel):
    id: str
    name: str
    email: str
    score: float

@router.post('/search_leads', response_model=List[SearchResult])
async def search_leads(payload: SearchPayload, user = Depends(get_current_user)):
    sb = supabase()
    query_vec = get_embedding(payload.query)
    if not query_vec:
        raise HTTPException(status_code=500, detail='Embedding failed')
    # Expect leads table to have embedding vector in column 'embedding'
    # Supabase can run RPC for similarity; here we fetch top N and compute cos sim client-side
    res = sb.table('leads').select('id,name,email,embedding').limit(200).execute()
    import math
    def cos(a, b):
        if not a or not b or len(a) != len(b):
            return -1.0
        dot = sum(x*y for x, y in zip(a, b))
        na = math.sqrt(sum(x*x for x in a))
        nb = math.sqrt(sum(x*x for x in b))
        if na == 0 or nb == 0:
            return -1.0
        return dot/(na*nb)
    results = []
    for row in res.data or []:
        sim = cos(query_vec, row.get('embedding') or [])
        results.append({ 'id': row['id'], 'name': row.get('name',''), 'email': row.get('email',''), 'score': sim })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:20]
