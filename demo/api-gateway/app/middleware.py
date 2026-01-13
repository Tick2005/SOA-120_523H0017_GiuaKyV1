from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, Response
import httpx
from app.config import settings

async def get_token_from_cookie(request: Request) -> str | None:
    return request.cookies.get("access_token")

async def validate_token(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_service_url}/api/auth/verify-token",
            json={"token": token},
            headers={"X-API-Key": settings.internal_api_key},
            timeout=10.0
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        result = response.json()
        if not result.get("valid"):
            raise HTTPException(status_code=401, detail=result.get("error", "Invalid or expired token"))
        return result.get("user", {})

async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # QUAN TRỌNG: OPTIONS requests phải được cho qua TRƯỚC để xử lý CORS
    if request.method == "OPTIONS":
        return await call_next(request)

    token = await get_token_from_cookie(request)
    
    # ============================================
    # PUBLIC API ENDPOINTS (Không cần JWT auth)
    # ============================================
    public_api_endpoints = [
        "/api/auth/login",           # Login endpoint
        "/api/auth/logout",          # Logout endpoint (chỉ cần xóa cookie)
        "/api/auth/verify-token",    # Internal endpoint - dùng API Key
    ]
    
    # ============================================
    # PUBLIC HTML PAGES (Không cần auth)
    # ============================================
    public_html_pages = [
        "/",                         # Homepage/Login page
        "/index.html",               # Login page
        "/header.html",              # Shared header component
        "/footer.html",              # Shared footer component
    ]
    
    # ============================================
    # PROTECTED HTML PAGES (Cho phép load, JS sẽ check auth)
    # ============================================
    # Các trang này cần auth nhưng phải cho phép load HTML
    # để JavaScript (auth-check.js) có thể chạy và redirect nếu không có auth
    protected_html_pages = [
        "/otp.html",                 # OTP verification page
        "/payment.html",             # Payment page
        "/profile.html",             # User profile page
        "/transactions.html",        # Transaction history page
        "/success.html",             # Payment success page
    ]
    
    # ============================================
    # SYSTEM ENDPOINTS (Không cần auth)
    # ============================================
    system_endpoints = [
        "/favicon.ico",              # Browser icon
        "/docs",                     # API documentation (Swagger)
        "/openapi.json",             # OpenAPI schema
        "/health",                   # Health check endpoint
    ]
    
    # ============================================
    # STATIC RESOURCES (Không cần auth)
    # ============================================
    static_prefixes = [
        "/css/",                     # Stylesheets
        "/js/",                      # JavaScript files
        "/img/",                     # Images
        "/static/",                  # Other static assets
    ]
    
    # ============================================
    # CHECK PUBLIC ACCESS
    # ============================================
    all_public_paths = (
        public_api_endpoints + 
        public_html_pages + 
        protected_html_pages +  # HTML pages cho phép load
        system_endpoints
    )
    
    if path in all_public_paths or any(path.startswith(prefix) for prefix in static_prefixes):
        return await call_next(request)

    if not token:
        return JSONResponse(status_code=401, content={"detail": "Missing access token"})

    try:
        user_info = await validate_token(token)
    except HTTPException as e:
        return JSONResponse(status_code=401, content={"detail": str(e.detail)})

    request.state.user = user_info
    request.state.token = token

    response = await call_next(request)
    return response

