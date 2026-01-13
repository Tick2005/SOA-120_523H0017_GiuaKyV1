from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class SearchRequest(BaseModel):
    """Request body for POST /search"""
    student_id: str = Field(..., description="Student ID to search for")

class TuitionResponse(BaseModel):
    """Single tuition response"""
    id: int
    student_id: str
    semester: int
    academic_year: str
    fee: float
    status: str
    canPay: Optional[bool] = None

class StudentInfo(BaseModel):
    """Student information"""
    student_id: str
    student_name: str
    student_email: str

class SearchResponse(BaseModel):
    """Response for POST /search"""
    student: StudentInfo
    all_tuitions: list[TuitionResponse]

class GetPayableRequest(BaseModel):
    """Request body for POST /get-payable (internal API)"""
    student_id: str = Field(..., description="Student ID to get payable tuition")

class GetPayableResponse(BaseModel):
    """Response for POST /get-payable (internal API)"""
    success: bool
    tuition: Optional[TuitionResponse] = None
    message: Optional[str] = None

class MarkPaidRequest(BaseModel):
    """Request body for POST /:id/mark-paid"""
    paid: bool = Field(True, description="Mark tuition as paid")

class MarkPaidResponse(BaseModel):
    """Response for POST /:id/mark-paid"""
    success: bool
    tuition: TuitionResponse

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
