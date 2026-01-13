from pydantic import BaseModel, Field
from typing import Optional

# Request Schemas
class IssueOTPRequest(BaseModel):
    """Request to issue OTP (PUBLIC API - from Frontend)"""
    student_id: str = Field(..., description="Student ID to pay tuition for")

class VerifyOTPRequest(BaseModel):
    """Request to verify OTP (INTERNAL API - from Payment Service)"""
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")

# Response Schemas
class TuitionInfo(BaseModel):
    """Tuition information"""
    id: int
    semester: int
    academic_year: str
    amount: float

class IssueOTPResponse(BaseModel):
    """Response for issuing OTP"""
    success: bool
    transaction_id: int
    tuition_info: TuitionInfo
    message: str
    expires_in_minutes: int

class VerifyOTPResponse(BaseModel):
    """Response for verifying OTP"""
    valid: bool
    transaction_id: Optional[int] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
