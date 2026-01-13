from pydantic import BaseModel, EmailStr
from typing import Optional
from decimal import Decimal

# Customer Schemas
class CustomerInfo(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    phone_number: str
    balance: float
    
    class Config:
        from_attributes = True

# Search Request (Internal)
class SearchRequest(BaseModel):
    username: str
    password: str

class SearchResponse(BaseModel):
    success: bool
    user: Optional[CustomerInfo] = None
    error: Optional[str] = None

# Deduct Balance Request (Internal)
class DeductBalanceRequest(BaseModel):
    customer_id: int
    amount: float
    transaction_code: str

class DeductBalanceResponse(BaseModel):
    success: bool
    new_balance: Optional[float] = None
    old_balance: Optional[float] = None
    error: Optional[str] = None
    current_balance: Optional[float] = None
    required_amount: Optional[float] = None

# Update Profile Request
class UpdateProfileRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

class UpdateProfileResponse(BaseModel):
    success: bool
    message: str
    user: Optional[CustomerInfo] = None
    error: Optional[str] = None
