from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer,  HTTPAuthorizationCredentials
from config import settings
from database import get_db
from sqlalchemy.orm import Session
from models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    # Make sure 'sub' is a string
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    encoded_jwt = jwt.encode(to_encode, "verysecure", algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    
    print(f"Attempting to decode token...")
    print(f"Token: {token[:20]}...{token[-20:]}") 

    print(f"SECRET_KEY: {settings.SECRET_KEY[:10]}...") 
    print(f"ALGORITHM: {settings.ALGORITHM}")
    
    payload = jwt.decode(token, "verysecure", algorithms=["HS256"])
    
    print(f"✓ Token decoded successfully!")
    print(f"Payload: {payload}")
    
    return payload
        
    # except jwt.ExpiredSignatureError as e:
    #     print(f"✗ ERROR: Token has expired - {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Token has expired",
    #     )
    # except jwt.InvalidTokenError as e:
    #     print(f"✗ ERROR: Invalid token - {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token format",
    #     )
    # except JWTError as e:
    #     print(f"✗ ERROR: JWT Error - {type(e).__name__}: {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid authentication credentials",
    #     )
    # except Exception as e:
    #     print(f"✗ ERROR: Unexpected error - {type(e).__name__}: {e}")
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Token verification failed",
    #     )

async def get_current_user(
    credentials:  HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    
    print(f"Credentials received: {credentials.credentials}")
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)

    print(f"Verify token value: {payload}")
    
    user_id: int = int(payload.get("sub"))
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    
    return user
