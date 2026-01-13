from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from . import models, schemas
from .database import get_db
from .config import INTERNAL_API_KEY

router = APIRouter()

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Verify API key for internal endpoints"""
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid API Key"
        )
    return True

@router.post("/search", response_model=schemas.SearchResponse)
def search_student(
    request: schemas.SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search student and return all tuitions with canPay flag.
    Only the oldest unpaid tuition will have canPay = true.
    """
    # Query all tuitions for this student, ordered by academic_year and semester
    tuitions = db.query(models.Tuition).filter(
        models.Tuition.student_id == request.student_id
    ).order_by(
        models.Tuition.academic_year.asc(),
        models.Tuition.semester.asc()
    ).all()

    if not tuitions:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID {request.student_id} not found"
        )

    # Get student info from first tuition record
    first_tuition = tuitions[0]
    student_info = schemas.StudentInfo(
        student_id=first_tuition.student_id,
        student_name=first_tuition.student_name,
        student_email=first_tuition.student_email
    )

    # Find first unpaid tuition (oldest)
    unpaid_tuitions = [t for t in tuitions if t.status == models.TuitionStatus.UNPAID]
    first_unpaid_id = unpaid_tuitions[0].id if unpaid_tuitions else None

    # Convert to response format with canPay flag
    tuition_responses = []
    for tuition in tuitions:
        tuition_dict = tuition.to_dict(include_can_pay=True)
        # Set canPay = true only for the first unpaid tuition
        tuition_dict["canPay"] = (tuition.id == first_unpaid_id)
        tuition_responses.append(schemas.TuitionResponse(**tuition_dict))

    return schemas.SearchResponse(
        student=student_info,
        all_tuitions=tuition_responses
    )

@router.post("/get-payable", response_model=schemas.GetPayableResponse)
def get_payable_tuition(
    request: schemas.GetPayableRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    INTERNAL API: Get the payable tuition (oldest unpaid) for a student.
    Used by Payment Service to get tuition info without student details.
    """
    # Query all tuitions for this student, ordered by academic_year and semester
    tuitions = db.query(models.Tuition).filter(
        models.Tuition.student_id == request.student_id
    ).order_by(
        models.Tuition.academic_year.asc(),
        models.Tuition.semester.asc()
    ).all()

    if not tuitions:
        raise HTTPException(
            status_code=404,
            detail=f"Student with ID {request.student_id} not found"
        )

    # Find first unpaid tuition
    unpaid_tuitions = [t for t in tuitions if t.status == models.TuitionStatus.UNPAID]
    
    if not unpaid_tuitions:
        return schemas.GetPayableResponse(
            success=True,
            tuition=None,
            message="All tuitions are paid"
        )

    # Return only the tuition info (no student info)
    payable_tuition = unpaid_tuitions[0]
    tuition_response = schemas.TuitionResponse(**payable_tuition.to_dict())

    return schemas.GetPayableResponse(
        success=True,
        tuition=tuition_response
    )

@router.post("/{tuition_id}/mark-paid", response_model=schemas.MarkPaidResponse)
def mark_tuition_paid(
    tuition_id: int,
    request: schemas.MarkPaidRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    INTERNAL API: Mark a tuition as paid.
    Called by Payment Service after successful payment.
    """
    # Start transaction
    try:
        # Get tuition with row lock
        tuition = db.query(models.Tuition).filter(
            models.Tuition.id == tuition_id
        ).with_for_update().first()

        if not tuition:
            raise HTTPException(
                status_code=404,
                detail=f"Tuition with ID {tuition_id} not found"
            )

        # Check if already paid
        if tuition.status == models.TuitionStatus.PAID:
            raise HTTPException(
                status_code=400,
                detail=f"Tuition {tuition_id} is already marked as paid"
            )

        # Update tuition
        tuition.fee = 0
        tuition.status = models.TuitionStatus.PAID

        db.commit()
        db.refresh(tuition)

        return schemas.MarkPaidResponse(
            success=True,
            tuition=schemas.TuitionResponse(**tuition.to_dict())
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
