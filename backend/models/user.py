from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    plan: str = "free"
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    plan: Optional[str] = None
    full_name: Optional[str] = None

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    stripe_customer_id: Optional[str] = None
    subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None
    payment_status: Optional[str] = None
    last_payment_date: Optional[datetime] = None

    class Config:
        from_attributes = True

