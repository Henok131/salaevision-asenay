import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from utils.email_utils import send_followup
from routes.auth import get_current_user

router = APIRouter()

FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@asenaytech.com')


class FollowUp(BaseModel):
    to_email: EmailStr
    subject: str
    content: str


@router.post("/followup")
async def send_followup_email(payload: FollowUp, user=Depends(get_current_user)):
    try:
        res = send_followup(payload.to_email, payload.subject, payload.content, FROM_EMAIL)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
