from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from services.supabase_client import get_supabase_client

router = APIRouter()

def render_embed_html(dashboard: dict) -> str:
    # Minimal HTML with dark theme. In practice, render a small chart from dashboard['data']
    name = dashboard.get('name', 'SalesVision Chart')
    return f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1" />
  <title>{name}</title>
  <style>
    body {{ margin:0; background:#0b1020; color:#e5e7eb; font-family: Inter, system-ui, -apple-system, sans-serif; }}
    .wrap {{ padding: 12px; }}
    .card {{ background: rgba(17, 24, 39, 0.8); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; padding: 12px; }}
    h1 {{ font-size: 16px; margin: 0 0 8px 0; color: #fff; }}
    .meta {{ font-size: 12px; color:#9ca3af; margin-bottom:8px; }}
    .chart {{ height: 360px; border: 1px dashed rgba(255,255,255,0.12); border-radius: 8px; display:flex; align-items:center; justify-content:center; color:#94a3b8; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"card\">
      <h1>{name}</h1>
      <div class=\"meta\">Public embed via SalesVision XAI-360</div>
      <div class=\"chart\">Chart rendering placeholder</div>
    </div>
  </div>
</body>
</html>
"""

@router.get("/{public_id}", response_class=HTMLResponse)
def get_embedded_chart(public_id: str):
    supabase = get_supabase_client()
    resp = (
        supabase
        .table('dashboards')
        .select('*')
        .eq('public_id', public_id)
        .eq('is_public', True)
        .limit(1)
        .execute()
    )
    if not resp.data:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    html = render_embed_html(resp.data[0])
    return HTMLResponse(content=html)
