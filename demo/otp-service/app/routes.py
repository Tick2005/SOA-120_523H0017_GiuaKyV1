from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import httpx

from .database import get_db
from .models import OTP
from .schemas import (
    IssueOTPRequest, IssueOTPResponse,
    VerifyOTPRequest, VerifyOTPResponse,
    TuitionInfo, ErrorResponse
)
from .config import (
    INTERNAL_API_KEY, OTP_EXPIRY_MINUTES, OTP_LENGTH,
    PAYMENT_SERVICE_URL, CUSTOMER_SERVICE_URL, STUDENT_SERVICE_URL
)
from .utils import generate_otp, send_otp_email

router = APIRouter(prefix="/api/otp", tags=["OTP"])

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """Verify API Key for internal endpoints"""
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid API Key"
        )
    return True

@router.post("/issue", response_model=IssueOTPResponse)
async def issue_otp(
    request: IssueOTPRequest,
    x_customer_id: int = Header(..., alias="X-Customer-ID"),
    db: Session = Depends(get_db)
):
    """
    Issue OTP for payment (PUBLIC API - called by Frontend)
    
    Flow:
    1. Get customer_id from JWT (via X-Customer-ID header)
    2. Call Payment Service /create to create transaction
    3. Expire old OTPs for this transaction (if any)
    4. Generate new OTP
    5. Get customer email
    6. Get tuition info
    7. Send OTP email
    8. Return transaction_id and tuition_info
    """
    try:
        # Step 1.5: Cleanup old pending transactions for this customer+student (resend OTP scenario)
        print(f"[CLEANUP START] Attempting cleanup for customer {x_customer_id}, student {request.student_id}", flush=True)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                cleanup_url = f"{PAYMENT_SERVICE_URL}/api/transactions/cleanup-pending"
                cleanup_payload = {
                    "customer_id": x_customer_id,
                    "student_id": request.student_id
                }
                print(f"[CLEANUP] Calling {cleanup_url} with payload: {cleanup_payload}", flush=True)
                
                cleanup_response = await client.post(
                    cleanup_url,
                    json=cleanup_payload,
                    headers={"X-API-Key": INTERNAL_API_KEY}
                )
                
                print(f"[CLEANUP] Response status: {cleanup_response.status_code}", flush=True)
                
                if cleanup_response.status_code == 200:
                    cleanup_data = cleanup_response.json()
                    print(f"[CLEANUP] Response data: {cleanup_data}", flush=True)
                    
                    if cleanup_data.get("deleted_count", 0) > 0:
                        print(f"[RESEND] Cleaned up {cleanup_data['deleted_count']} old transactions for student {request.student_id}", flush=True)
                        
                        # Expire old OTPs for deleted transactions
                        if cleanup_data.get("transaction_ids"):
                            for old_trans_id in cleanup_data["transaction_ids"]:
                                db.query(OTP).filter(
                                    OTP.transaction_id == old_trans_id,
                                    OTP.status == "active"
                                ).update({"status": "expired"})
                            db.commit()
                            print(f"[CLEANUP] Expired OTPs for transactions: {cleanup_data['transaction_ids']}", flush=True)
                    else:
                        print(f"[CLEANUP] No old transactions to delete", flush=True)
                else:
                    print(f"[CLEANUP ERROR] Non-200 status: {cleanup_response.status_code}, body: {cleanup_response.text}", flush=True)
        except Exception as e:
            print(f"[CLEANUP ERROR] Failed to cleanup old transactions: {str(e)}", flush=True)
            import traceback
            print(f"[CLEANUP ERROR] Traceback: {traceback.format_exc()}", flush=True)
        
        # Step 2: Create NEW transaction via Payment Service
        async with httpx.AsyncClient(timeout=30.0) as client:
            transaction_response = await client.post(
                f"{PAYMENT_SERVICE_URL}/api/transactions/create",
                json={
                    "customer_id": x_customer_id,
                    "student_id": request.student_id
                },
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if transaction_response.status_code != 200:
                error_detail = transaction_response.json().get("detail", "Failed to create transaction")
                raise HTTPException(
                    status_code=transaction_response.status_code,
                    detail=error_detail
                )
            
            transaction_data = transaction_response.json()
            transaction_id = transaction_data["id"]
            tuition_id = transaction_data["tuition_id"]
            amount = transaction_data["amount"]
        
        otp_code = generate_otp(OTP_LENGTH)
        
        otp = OTP(
            otp_code=otp_code,
            transaction_id=transaction_id,
            status="active"
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)
        
        # Step 5: Get customer email
        async with httpx.AsyncClient(timeout=30.0) as client:
            customer_response = await client.get(
                f"{CUSTOMER_SERVICE_URL}/api/customers/me",
                headers={"X-Customer-ID": str(x_customer_id)}
            )
            
            if customer_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get customer info"
                )
            
            customer_data = customer_response.json()
            customer_email = customer_data.get("email")
            customer_name = customer_data.get("username", "Customer")
        
        # Step 6: Get tuition info
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get payable tuition to get semester and academic_year
            tuition_response = await client.post(
                f"{STUDENT_SERVICE_URL}/get-payable",
                json={"student_id": request.student_id},
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if tuition_response.status_code == 200:
                tuition_data = tuition_response.json()
                if tuition_data.get("success") and tuition_data.get("tuition"):
                    tuition = tuition_data["tuition"]
                    semester = tuition.get("semester", 1)
                    academic_year = tuition.get("academic_year", "2024-2025")
                else:
                    semester = 1
                    academic_year = "2024-2025"
            else:
                semester = 1
                academic_year = "2024-2025"
        
        # Step 7: Send OTP email
        tuition_info_for_email = {
            "semester": semester,
            "academic_year": academic_year,
            "amount": amount
        }
        
        email_sent = send_otp_email(
            recipient=customer_email,
            otp_code=otp_code,
            user_name=customer_name,
            tuition_info=tuition_info_for_email,
            expires_in_minutes=OTP_EXPIRY_MINUTES
        )
        
        if not email_sent:
            print(f"Warning: Failed to send OTP email to {customer_email}")
        
        # Step 8: Return response
        return IssueOTPResponse(
            success=True,
            transaction_id=transaction_id,
            tuition_info=TuitionInfo(
                id=tuition_id,
                semester=semester,
                academic_year=academic_year,
                amount=amount
            ),
            message="OTP đã được gửi qua email. Vui lòng kiểm tra hộp thư.",
            expires_in_minutes=OTP_EXPIRY_MINUTES
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to issue OTP: {str(e)}"
        )

@router.post("/verify", response_model=VerifyOTPResponse)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Verify OTP and mark as used (INTERNAL API - called by Payment Service)
    
    Flow:
    1. Find OTP by code with status 'active'
    2. Check if expired (created_at + 5 minutes < NOW)
    3. If valid: mark as 'used' and return transaction_id
    4. If invalid/expired: return error
    """
    try:
        # Step 1: Find OTP
        otp = db.query(OTP).filter(
            OTP.otp_code == request.otp_code,
            OTP.status == "active"
        ).first()
        
        if not otp:
            return VerifyOTPResponse(
                valid=False,
                error="OTP không hợp lệ"
            )
        
        # Step 2: Check if expired
        expiry_time = otp.created_at + timedelta(minutes=OTP_EXPIRY_MINUTES)
        if datetime.now() > expiry_time:
            # Mark as expired
            otp.status = "expired"
            db.commit()
            
            return VerifyOTPResponse(
                valid=False,
                error="OTP đã hết hạn"
            )
        
        # Step 3: OTP is valid - mark as used
        otp.status = "used"
        db.commit()
        
        return VerifyOTPResponse(
            valid=True,
            transaction_id=otp.transaction_id
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify OTP: {str(e)}"
        )
