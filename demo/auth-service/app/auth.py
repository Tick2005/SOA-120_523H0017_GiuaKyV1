from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from .config import settings

def create_access_token(data: Dict[str, Any]) -> str:
    """
    Tạo JWT access token
    
    Args:
        data: Dictionary chứa user info (user_id, username, email)
    
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify và decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload nếu valid, None nếu invalid
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
