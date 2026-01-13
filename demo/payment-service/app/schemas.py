from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

# Request Schemas
class CreateTransactionRequest(BaseModel):
    """Request to create a new transaction (INTERNAL - from OTP Service)"""
    customer_id: int = Field(..., description="Customer ID")
    student_id: str = Field(..., description="Student ID")

class ConfirmPaymentRequest(BaseModel):
    """Request to confirm payment with OTP (PUBLIC - from Frontend)"""
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    student_id: str = Field(..., description="Student ID")

# Response Schemas
class TuitionInfo(BaseModel):
    """Tuition information"""
    id: int
    semester: int
    academic_year: str
    amount: float

class TransactionResponse(BaseModel):
    """Transaction response"""
    id: int
    customer_id: int
    tuition_id: int
    amount: float
    status: str
    created_at: str
    
    class Config:
        from_attributes = True

class CreateTransactionResponse(BaseModel):
    """Response for creating transaction"""
    id: int
    customer_id: int
    tuition_id: int
    amount: float
    status: str
    created_at: str

class ConfirmPaymentResponse(BaseModel):
    """Response for confirming payment"""
    success: bool
    message: str
    transaction: TransactionResponse
    new_balance: float

class TransactionHistoryResponse(BaseModel):
    """Response for transaction history"""
    transactions: List[TransactionResponse]

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    current_balance: Optional[float] = None
    required_amount: Optional[float] = None
