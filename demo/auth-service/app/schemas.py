from pydantic import BaseModel, EmailStr
from typing import Optional

# Request Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class VerifyTokenRequest(BaseModel):
    token: str

# Response Schemas
class UserInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    balance: float

class LoginResponse(BaseModel):
    user: UserInfo

class LogoutResponse(BaseModel):
    success: bool
    message: str

class VerifyTokenResponse(BaseModel):
    valid: bool
    user: Optional[UserInfo] = None
    error: Optional[str] = None
    message: Optional[str] = None
