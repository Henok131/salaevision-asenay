from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from services.supabase_client import get_supabase_client

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
# All JWT configuration must come from environment variables
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
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
    if not SECRET_KEY:
        # Fail fast if JWT secret is not configured
        raise ValueError("JWT_SECRET_KEY must be set in the environment")
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

async def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return user data"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
        
        # Get user from Supabase
        supabase = get_supabase_client()
        result = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not result.data:
            return None
        
        user = result.data[0]
        return {
            "id": user["id"],
            "email": user["email"],
            "plan": user.get("plan", "free"),
            "created_at": user.get("created_at")
        }
        
    except JWTError:
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

async def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """Get current user from token"""
    return await verify_token(token)

