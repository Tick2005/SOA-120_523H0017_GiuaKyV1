from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional
import httpx
from datetime import datetime

from .database import get_db
from .models import Transaction
from .schemas import (
    CreateTransactionRequest, CreateTransactionResponse,
    ConfirmPaymentRequest, ConfirmPaymentResponse,
    TransactionHistoryResponse, TransactionResponse,
    ErrorResponse
)
from .config import (
    INTERNAL_API_KEY, CUSTOMER_SERVICE_URL,
    STUDENT_SERVICE_URL, OTP_SERVICE_URL, MAIL_SERVICE_URL
)
from .email_utils import send_invoice_email

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """Verify API Key for internal endpoints"""
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid API Key"
        )
    return True

@router.post("/create", response_model=CreateTransactionResponse)
async def create_transaction(
    request: CreateTransactionRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Create a new transaction (INTERNAL API - called by OTP Service)
    
    Flow:
    1. Call Student Service /get-payable to get tuition to pay
    2. Create transaction with status 'pending'
    3. Return transaction info
    """
    try:
        # Step 1: Get payable tuition from Student Service
        async with httpx.AsyncClient() as client:
            tuition_response = await client.post(
                f"{STUDENT_SERVICE_URL}/get-payable",
                json={"student_id": request.student_id},
                headers={"X-API-Key": INTERNAL_API_KEY},
                timeout=10.0
            )
            
            if tuition_response.status_code != 200:
                raise HTTPException(
                    status_code=tuition_response.status_code,
                    detail="Failed to get payable tuition from Student Service"
                )
            
            tuition_data = tuition_response.json()
            
            if not tuition_data.get("success"):
                raise HTTPException(
                    status_code=400,
                    detail=tuition_data.get("message", "No unpaid tuitions found")
                )
            
            tuition = tuition_data.get("tuition")
            if not tuition:
                raise HTTPException(
                    status_code=400,
                    detail="All tuitions are paid"
                )
        
        # Step 2: Create transaction
        transaction = Transaction(
            customer_id=request.customer_id,
            tuition_id=tuition["id"],
            amount=Decimal(str(tuition["fee"])),
            status="pending"
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Step 3: Return transaction info
        return CreateTransactionResponse(
            id=transaction.id,
            customer_id=transaction.customer_id,
            tuition_id=transaction.tuition_id,
            amount=float(transaction.amount),
            status=transaction.status,
            created_at=transaction.created_at.isoformat()
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create transaction: {str(e)}"
        )

@router.post("/confirm", response_model=ConfirmPaymentResponse)
async def confirm_payment(
    request: ConfirmPaymentRequest,
    x_customer_id: int = Header(..., alias="X-Customer-ID"),
    db: Session = Depends(get_db)
):
    """
    Confirm payment with OTP (PUBLIC API - called by Frontend)
    
    Flow:
    1. Get customer_id from JWT (via X-Customer-ID header)
    2. Verify OTP and get transaction_id (call OTP Service)
    3. Get transaction info
    4. Verify student_id matches (double-check)
    5. Get customer balance
    6. Verify balance sufficient
    7. Deduct balance from customer
    8. Mark tuition as paid
    9. Update transaction status to 'completed'
    10. Send invoice email
    11. Return success response
    """
    try:
        # Step 2: Verify OTP
        async with httpx.AsyncClient(timeout=30.0) as client:
            otp_response = await client.post(
                f"{OTP_SERVICE_URL}/api/otp/verify",
                json={"otp_code": request.otp_code},
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if otp_response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to verify OTP"
                )
            
            otp_data = otp_response.json()
            
            if not otp_data.get("valid"):
                raise HTTPException(
                    status_code=400,
                    detail=otp_data.get("error", "OTP không hợp lệ hoặc đã hết hạn")
                )
            
            transaction_id = otp_data.get("transaction_id")
        
        # Step 3: Get transaction info WITH EXCLUSIVE LOCK
        # This prevents race conditions - only 1 request can process this transaction at a time
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.status == "pending",
            Transaction.customer_id == x_customer_id
        ).with_for_update().first()
        
        if not transaction:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found or already processed"
            )
        
        # Step 4: Verify student_id matches (double-check)
        async with httpx.AsyncClient(timeout=30.0) as client:
            tuition_check = await client.post(
                f"{STUDENT_SERVICE_URL}/get-payable",
                json={"student_id": request.student_id},
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if tuition_check.status_code == 200:
                tuition_data = tuition_check.json()
                if tuition_data.get("success") and tuition_data.get("tuition"):
                    if tuition_data["tuition"]["id"] != transaction.tuition_id:
                        raise HTTPException(
                            status_code=400,
                            detail="Học phí cần thanh toán đã thay đổi, vui lòng tạo OTP mới"
                        )
        
        # Step 5: Get customer balance
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
            current_balance = customer_data.get("balance", 0)
        
        # Step 6: Verify balance sufficient
        if current_balance < float(transaction.amount):
            raise HTTPException(
                status_code=400,
                detail=f"Số dư không đủ. Số dư hiện tại: {current_balance:,.0f}đ, Cần: {float(transaction.amount):,.0f}đ"
            )
        
        # Step 7: Deduct balance from customer
        async with httpx.AsyncClient(timeout=30.0) as client:
            deduct_response = await client.post(
                f"{CUSTOMER_SERVICE_URL}/api/customers/deduct-balance",
                json={
                    "customer_id": x_customer_id,
                    "amount": float(transaction.amount),
                    "transaction_code": f"TXN{transaction.id:08d}"
                },
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if deduct_response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to deduct balance"
                )
            
            deduct_data = deduct_response.json()
            
            if not deduct_data.get("success"):
                raise HTTPException(
                    status_code=400,
                    detail=deduct_data.get("error", "Failed to deduct balance")
                )
            
            new_balance = deduct_data.get("new_balance")
        
        # Step 8: Mark tuition as paid
        async with httpx.AsyncClient(timeout=30.0) as client:
            mark_paid_response = await client.post(
                f"{STUDENT_SERVICE_URL}/{transaction.tuition_id}/mark-paid",
                json={"paid": True},
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if mark_paid_response.status_code != 200:
                # TODO: Rollback logic - refund customer balance
                # Currently Customer Service doesn't have refund endpoint
                # Manual refund may be required
                raise HTTPException(
                    status_code=500,
                    detail="Failed to mark tuition as paid. Customer balance was deducted but tuition not marked as paid. Manual intervention required."
                )
        
        # Step 9: Update transaction status
        transaction.status = "completed"
        db.commit()
        db.refresh(transaction)
        
        # Step 10: Send invoice email (fire-and-forget, don't wait)
        try:
            # Send invoice email directly using email_utils (no need to call Mail Service)
            send_invoice_email(
                recipient=customer_data.get("email"),
                customer_name=customer_data.get("username", "Customer"),
                transaction_id=transaction.id,
                transaction_code=f"TXN{transaction.id:08d}",
                tuition_id=transaction.tuition_id,
                amount=float(transaction.amount),
                new_balance=new_balance,
                payment_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            print(f"Failed to send invoice email: {str(e)}")
            # Don't fail the transaction if email fails
        
        # Step 11: Return success
        return ConfirmPaymentResponse(
            success=True,
            message="Thanh toán thành công",
            transaction=TransactionResponse(
                id=transaction.id,
                customer_id=transaction.customer_id,
                tuition_id=transaction.tuition_id,
                amount=float(transaction.amount),
                status=transaction.status,
                created_at=transaction.created_at.isoformat()
            ),
            new_balance=new_balance
        )
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Payment confirmation failed: {str(e)}"
        )

@router.post("/cancel")
async def cancel_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Delete a pending transaction (INTERNAL API - called by OTP Service scheduler or Frontend)
    
    Flow:
    1. Find transaction by ID with status 'pending'
    2. Delete the transaction from database
    3. Call OTP Service to expire associated OTP (best-effort)
    4. Return success
    """
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.status == "pending"
        ).first()
        
        if transaction:
            # Delete transaction instead of marking as cancelled
            db.delete(transaction)
            db.commit()
            
            # Try to expire OTP in OTP Service
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        f"{OTP_SERVICE_URL}/api/otp/expire-by-transaction",
                        params={"transaction_id": transaction_id},
                        headers={"X-API-Key": INTERNAL_API_KEY}
                    )
            except Exception as e:
                print(f"Warning: Failed to expire OTP for transaction {transaction_id}: {str(e)}")
        
        return {
            "success": True,
            "message": "Transaction deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete transaction: {str(e)}"
        )

@router.post("/cleanup-pending")
async def cleanup_pending_transactions(
    request: dict,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Cleanup old pending transactions for customer+student (INTERNAL API - called by OTP Service on resend)
    
    This handles resend OTP scenario:
    - User clicks "Resend OTP" for same student payment
    - We need to delete old pending transaction
    - System will create new transaction with new ID
    - Old OTP will be expired
    - New OTP will be created
    
    Flow:
    1. Get payable tuition for student_id
    2. Find all pending transactions for customer_id + tuition_id
    3. Delete those old transactions
    4. Return deleted transaction IDs (so OTP Service can expire associated OTPs)
    """
    try:
        customer_id = request.get("customer_id")
        student_id = request.get("student_id")
        
        if not customer_id or not student_id:
            raise HTTPException(status_code=400, detail="Missing customer_id or student_id")
        
        # Get payable tuition to find tuition_id
        async with httpx.AsyncClient(timeout=10.0) as client:
            tuition_response = await client.post(
                f"{STUDENT_SERVICE_URL}/get-payable",
                json={"student_id": student_id},
                headers={"X-API-Key": INTERNAL_API_KEY}
            )
            
            if tuition_response.status_code != 200:
                return {
                    "success": True,
                    "deleted_count": 0,
                    "transaction_ids": [],
                    "message": "No payable tuition found"
                }
            
            tuition_data = tuition_response.json()
            if not tuition_data.get("success") or not tuition_data.get("tuition"):
                return {
                    "success": True,
                    "deleted_count": 0,
                    "transaction_ids": [],
                    "message": "No payable tuition found"
                }
            
            tuition_id = tuition_data["tuition"]["id"]
        
        # Find and delete old pending transactions for same customer + tuition
        old_transactions = db.query(Transaction).filter(
            Transaction.customer_id == customer_id,
            Transaction.tuition_id == tuition_id,
            Transaction.status == "pending"
        ).all()
        
        deleted_ids = [trans.id for trans in old_transactions]
        
        for trans in old_transactions:
            db.delete(trans)
        
        if old_transactions:
            db.commit()
            print(f"[CLEANUP] Deleted {len(old_transactions)} old pending transactions (IDs: {deleted_ids}) for customer {customer_id}, student {student_id}")
        
        return {
            "success": True,
            "deleted_count": len(old_transactions),
            "transaction_ids": deleted_ids,
            "message": f"Deleted {len(old_transactions)} pending transactions"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup pending transactions: {str(e)}"
        )

@router.get("/history", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    x_customer_id: int = Header(..., alias="X-Customer-ID"),
    db: Session = Depends(get_db)
):
    """
    Get transaction history for current customer (PUBLIC API)
    
    Flow:
    1. Get customer_id from JWT (via X-Customer-ID header)
    2. Query all transactions for this customer
    3. Return transaction list
    """
    try:
        transactions = db.query(Transaction).filter(
            Transaction.customer_id == x_customer_id
        ).order_by(Transaction.created_at.desc()).all()
        
        return TransactionHistoryResponse(
            transactions=[
                TransactionResponse(
                    id=t.id,
                    customer_id=t.customer_id,
                    tuition_id=t.tuition_id,
                    amount=float(t.amount),
                    status=t.status,
                    created_at=t.created_at.isoformat()
                )
                for t in transactions
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get transaction history: {str(e)}"
        )
