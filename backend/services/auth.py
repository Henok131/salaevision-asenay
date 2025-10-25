from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from services.supabase_client import get_supabase_client, get_supabase_admin_client

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify token and return user data.
    Supports both app-issued JWT and Supabase session JWT.
    """
    # First, try to verify as app-issued JWT
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise JWTError("Missing subject")

        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            return None

        user = result.data[0]
        return {
            "id": user["id"],
            "email": user["email"],
            "plan": user.get("plan", "free"),
            "tokens_remaining": user.get("tokens_remaining"),
            "org_id": user.get("org_id"),
            "role": user.get("role", "viewer"),
            "created_at": user.get("created_at"),
        }
    except JWTError:
        pass
    except Exception as e:
        # Fall through to Supabase verification on any unexpected error
        print(f"App JWT verification error: {e}")

    # Fallback: verify Supabase session JWT via Supabase Admin API
    try:
        supabase_client = get_supabase_client()
        resp = supabase_client.auth.get_user(token)
        supabase_user = getattr(resp, "user", None)
        if not supabase_user:
            return None

        user_id = supabase_user.id
        email = supabase_user.email

        # Ensure presence in users table (id, email, plan) using admin privileges
        try:
            admin = get_supabase_admin_client()
            # Upsert basic user profile
            admin.table("users").upsert({
                "id": user_id,
                "email": email,
                "plan": "free",
            }, on_conflict="id").execute()
        except Exception as e:
            print(f"Upsert users table failed or RLS blocked: {e}")

        # Fetch user profile (ignore if not present)
        try:
            result = supabase_client.table("users").select("*").eq("id", user_id).execute()
            profile = result.data[0] if result.data else {"id": user_id, "email": email, "plan": "free", "tokens_remaining": 200}
        except Exception:
            profile = {"id": user_id, "email": email, "plan": "free", "tokens_remaining": 200}

        return {
            "id": profile["id"],
            "email": profile.get("email", email),
            "plan": profile.get("plan", "free"),
            "tokens_remaining": profile.get("tokens_remaining", 200),
            "org_id": profile.get("org_id"),
            "role": profile.get("role", "viewer"),
            "created_at": profile.get("created_at"),
        }
    except Exception as e:
        print(f"Supabase JWT verification error: {e}")
        return None

async def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """Get current user from token"""
    return await verify_token(token)

