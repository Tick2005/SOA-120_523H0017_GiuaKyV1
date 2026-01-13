from fastapi import APIRouter, HTTPException, Response, Header
from fastapi.responses import JSONResponse
import httpx
from .schemas import (
    LoginRequest, LoginResponse, LogoutResponse,
    VerifyTokenRequest, VerifyTokenResponse, UserInfo
)
from .auth import create_access_token, verify_token
from .config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response):
    """
    Đăng nhập vào hệ thống
    
    Flow:
    1. Nhận username/password từ request
    2. Gọi Customer Service POST /search để verify credentials
    3. Nếu valid: Generate JWT, set cookie, return user info
    4. Nếu invalid: Return 401 Unauthorized
    """
    # Gọi Customer Service để verify credentials
    async with httpx.AsyncClient() as client:
        try:
            customer_response = await client.post(
                f"{settings.CUSTOMER_SERVICE_URL}/api/customers/search",
                json={
                    "username": request.username,
                    "password": request.password
                },
                headers={
                    "X-API-Key": settings.INTERNAL_API_KEY
                },
                timeout=10.0
            )
            
            if customer_response.status_code != 200:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid username or password"
                )
            
            customer_data = customer_response.json()
            
            if not customer_data.get("success"):
                raise HTTPException(
                    status_code=401,
                    detail=customer_data.get("error", "Invalid credentials")
                )
            
            user_data = customer_data.get("user")
            
            # Generate JWT token
            token_data = {
                "user_id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"]
            }
            access_token = create_access_token(token_data)
            
            # Set JWT token in HttpOnly cookie
            response.set_cookie(
                key=settings.COOKIE_NAME,
                value=access_token,
                httponly=settings.COOKIE_HTTPONLY,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
                max_age=settings.COOKIE_MAX_AGE,
                path="/"
            )
            
            # Return user info (NOT token - already in cookie)
            return LoginResponse(
                user=UserInfo(
                    id=user_data["id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    balance=user_data["balance"]
                )
            )
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Customer Service unavailable: {str(e)}"
            )

@router.post("/logout", response_model=LogoutResponse)
async def logout(response: Response, access_token: str = Header(None, alias="Cookie")):
    """
    Đăng xuất khỏi hệ thống
    
    Flow:
    1. Nhận JWT token từ cookie header
    2. Xóa cookie bằng cách set Max-Age=0
    3. Return success message
    """
    # Xóa cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value="",
        httponly=settings.COOKIE_HTTPONLY,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=0,  # Xóa cookie ngay lập tức
        path="/"
    )
    
    return LogoutResponse(
        success=True,
        message="Logged out successfully"
    )

@router.post("/verify-token", response_model=VerifyTokenResponse)
async def verify_jwt_token(
    request: VerifyTokenRequest,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """
    Verify JWT token (INTERNAL ONLY - API Gateway sử dụng)
    
    Flow:
    1. Verify API Key
    2. Decode và verify JWT token
    3. Return user info nếu valid
    4. Return error nếu invalid/expired
    """
    # Verify API Key
    if x_api_key != settings.INTERNAL_API_KEY:
        return VerifyTokenResponse(
            valid=False,
            error="Unauthorized: Invalid API Key"
        )
    
    # Verify JWT token
    payload = verify_token(request.token)
    
    if payload is None:
        return VerifyTokenResponse(
            valid=False,
            error="Invalid token",
            message="Token signature verification failed"
        )
    
    # Check if token has required fields
    if "user_id" not in payload or "username" not in payload or "email" not in payload:
        return VerifyTokenResponse(
            valid=False,
            error="Invalid token",
            message="Token missing required fields"
        )
    
    # Token is valid - return user info
    return VerifyTokenResponse(
        valid=True,
        user=UserInfo(
            id=payload["user_id"],
            username=payload["username"],
            email=payload["email"],
            balance=0  # Balance không được lưu trong JWT, phải fetch từ Customer Service
        )
    )
