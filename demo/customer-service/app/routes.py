from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from decimal import Decimal
from .database import get_db
from .models import Customer
from .schemas import (
    CustomerInfo, SearchRequest, SearchResponse,
    DeductBalanceRequest, DeductBalanceResponse,
    UpdateProfileRequest, UpdateProfileResponse
)
from .config import settings

router = APIRouter(prefix="/api/customers", tags=["Customers"])

def verify_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Dependency to verify API Key for internal endpoints
    """
    if x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid API Key"
        )
    return True

@router.get("/me", response_model=CustomerInfo)
async def get_current_customer(
    x_customer_id: int = Header(..., alias="X-Customer-ID"),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin customer hiện tại đang đăng nhập
    
    Flow:
    1. API Gateway đã verify JWT và inject X-Customer-ID vào header
    2. Query database để lấy customer info mới nhất
    3. Return customer info (bao gồm balance)
    """
    customer = db.query(Customer).filter(Customer.id == x_customer_id).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    return CustomerInfo(
        id=customer.id,
        username=customer.username,
        email=customer.email,
        full_name=customer.full_name,
        phone_number=customer.phone_number,
        balance=float(customer.balance)
    )

@router.post("/search", response_model=SearchResponse)
async def search_customer(
    request: SearchRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Tìm kiếm customer theo username/password (INTERNAL ONLY)
    
    Flow:
    1. Verify API Key
    2. Query database để tìm customer theo username
    3. Verify password (plain text comparison)
    4. Return user info nếu hợp lệ
    """
    # Find customer by username
    customer = db.query(Customer).filter(Customer.username == request.username).first()
    
    if not customer:
        return SearchResponse(
            success=False,
            error="Invalid username or password"
        )
    
    # Verify password (plain text comparison)
    if customer.password != request.password:
        return SearchResponse(
            success=False,
            error="Invalid username or password"
        )
    
    # Return customer info
    return SearchResponse(
        success=True,
        user=CustomerInfo(
            id=customer.id,
            username=customer.username,
            email=customer.email,
            full_name=customer.full_name,
            phone_number=customer.phone_number,
            balance=float(customer.balance)
        )
    )

@router.put("/update-profile", response_model=UpdateProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    x_customer_id: int = Header(..., alias="X-Customer-ID"),
    db: Session = Depends(get_db)
):
    """
    Cập nhật thông tin profile của customer
    
    Flow:
    1. Get customer_id from JWT (via X-Customer-ID header)
    2. Verify current password if changing password
    3. Check username/email uniqueness if changing
    4. Update fields
    5. Return updated user info
    """
    try:
        customer = db.query(Customer).filter(
            Customer.id == x_customer_id
        ).first()
        
        if not customer:
            return UpdateProfileResponse(
                success=False,
                message="Customer not found",
                error="Customer not found"
            )
        
        # If changing password, verify current password first
        if request.new_password:
            if not request.current_password:
                return UpdateProfileResponse(
                    success=False,
                    message="Current password is required to change password",
                    error="Current password is required"
                )
            
            if customer.password != request.current_password:
                return UpdateProfileResponse(
                    success=False,
                    message="Current password is incorrect",
                    error="Invalid current password"
                )
            
            # Update password
            customer.password = request.new_password
        
        # Check username uniqueness if changing
        if request.username and request.username != customer.username:
            existing = db.query(Customer).filter(
                Customer.username == request.username,
                Customer.id != x_customer_id
            ).first()
            
            if existing:
                return UpdateProfileResponse(
                    success=False,
                    message="Username already exists",
                    error="Username already taken"
                )
            
            customer.username = request.username
        
        # Check email uniqueness if changing
        if request.email and request.email != customer.email:
            existing = db.query(Customer).filter(
                Customer.email == request.email,
                Customer.id != x_customer_id
            ).first()
            
            if existing:
                return UpdateProfileResponse(
                    success=False,
                    message="Email already exists",
                    error="Email already taken"
                )
            
            customer.email = request.email
        
        # Update other fields
        if request.full_name:
            customer.full_name = request.full_name
        
        if request.phone_number:
            customer.phone_number = request.phone_number
        
        # Commit changes
        db.commit()
        db.refresh(customer)
        
        return UpdateProfileResponse(
            success=True,
            message="Profile updated successfully",
            user=CustomerInfo(
                id=customer.id,
                username=customer.username,
                email=customer.email,
                full_name=customer.full_name,
                phone_number=customer.phone_number,
                balance=float(customer.balance)
            )
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.post("/deduct-balance", response_model=DeductBalanceResponse, response_model_exclude_none=True)
async def deduct_balance(
    request: DeductBalanceRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Trừ tiền từ tài khoản customer (INTERNAL ONLY - Payment Service gọi)
    
    Flow:
    1. Verify API Key
    2. BEGIN TRANSACTION
    3. SELECT FOR UPDATE (row lock)
    4. Kiểm tra balance >= amount
    5. UPDATE balance nếu đủ tiền
    6. COMMIT hoặc ROLLBACK
    """
    try:
        # Begin transaction
        customer = db.query(Customer).filter(
            Customer.id == request.customer_id
        ).with_for_update().first()
        
        if not customer:
            db.rollback()
            return DeductBalanceResponse(
                success=False,
                error="Customer not found"
            )
        
        old_balance = float(customer.balance)
        
        # Check if balance is sufficient
        if customer.balance < Decimal(str(request.amount)):
            db.rollback()
            return DeductBalanceResponse(
                success=False,
                error="Insufficient balance",
                current_balance=float(customer.balance),
                required_amount=request.amount
            )
        
        # Deduct balance (convert float to Decimal for proper arithmetic)
        customer.balance = customer.balance - Decimal(str(request.amount))
        
        # Commit transaction
        db.commit()
        db.refresh(customer)
        
        new_balance = float(customer.balance)
        
        return DeductBalanceResponse(
            success=True,
            new_balance=new_balance,
            old_balance=old_balance
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deduct balance: {str(e)}"
        )
