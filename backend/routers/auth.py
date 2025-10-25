from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import os
from services.supabase_client import get_supabase_client
from services.auth import create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

@router.post("/login")
async def login(login_data: LoginRequest):
    """
    Authenticate user with email and password
    """
    try:
        supabase = get_supabase_client()
        
        # Authenticate with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": response.user.id})
        
        # Get user profile
        user_profile = {
            "id": response.user.id,
            "email": response.user.email,
            "created_at": response.user.created_at,
            "plan": "free"  # Default plan
        }
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_profile
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/signup")
async def signup(signup_data: SignupRequest):
    """
    Register new user
    """
    try:
        supabase = get_supabase_client()
        
        # Create user in Supabase
        response = supabase.auth.sign_up({
            "email": signup_data.email,
            "password": signup_data.password,
            "options": {
                "data": {
                    "full_name": signup_data.full_name or ""
                }
            }
        })
        
        if not response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        # Create user profile in database
        user_profile = {
            "id": response.user.id,
            "email": response.user.email,
            "plan": "free",
            "created_at": response.user.created_at
        }
        
        # Insert user into users table
        supabase.table("users").insert(user_profile).execute()
        
        # Create JWT token
        access_token = create_access_token(data={"sub": response.user.id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_profile
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user
    """
    try:
        # In a real implementation, you might want to blacklist the token
        # For now, we'll just return success
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current user information
    """
    try:
        user = await verify_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return {"user": user}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token
    """
    try:
        user = await verify_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Create new token
        new_token = create_access_token(data={"sub": user["id"]})
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            user=user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token refresh failed: {str(e)}"
        )

