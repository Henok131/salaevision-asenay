from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routes.auth import get_current_user
from integrations.integration_controller import integration_client

router = APIRouter()

class ConnectPayload(BaseModel):
  tool: str

@router.post('/integrations/connect')
async def connect_integration(payload: ConnectPayload, user = Depends(get_current_user)):
  try:
    client = integration_client.connect_tool(payload.tool)
    return { 'tool': payload.tool, 'connected': True, 'details': client }
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))

@router.get('/integrations/status')
async def integrations_status(user = Depends(get_current_user)):
  return integration_client.get_status()
