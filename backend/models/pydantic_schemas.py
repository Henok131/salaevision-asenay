from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = Field(pattern=r"^(admin|analyst|viewer)$")
    org_id: str


class AcceptInviteRequest(BaseModel):
    token: str


class TogglePublicRequest(BaseModel):
    is_public: bool
    dashboard_id: Optional[str] = None
