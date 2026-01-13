from fastapi import APIRouter, Request, HTTPException, Response
import httpx
from fastapi.responses import JSONResponse
from app.config import settings
import json

router = APIRouter()

SERVICE_MAP = {
    "/api/auth": settings.auth_service_url,
    "/api/customers": settings.customer_service_url,
    "/api/students": settings.tuition_service_url,
    "/api/tuitions": settings.tuition_service_url,
    "/api/transactions": settings.payment_service_url,
    "/api/otp": settings.otp_service_url,
}

async def proxy_request(request: Request, target_url: str, add_api_key: bool = False, modify_body=None, skip_query_params: bool = False):
    """
    Proxy request to backend service
    
    Args:
        request: FastAPI request object
        target_url: Target URL to proxy to (may include query string)
        add_api_key: Whether to add internal API key
        modify_body: Optional function to modify request body before sending
        skip_query_params: If True, don't add request.query_params (useful when URL already has query string)
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        body = await request.body()
        
        # Modify body if needed
        if modify_body and body:
            try:
                body_data = json.loads(body)
                body_data = modify_body(body_data)
                body = json.dumps(body_data).encode()
            except:
                pass

        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ["host", "content-length"]
        }

        # Add API key for internal endpoints
        if add_api_key:
            headers["X-API-Key"] = settings.internal_api_key

        if hasattr(request.state, "token"):
            headers["Cookie"] = f"access_token={request.state.token}"

        if hasattr(request.state, "user"):
            user_id = request.state.user.get("id") or request.state.user.get("user_id")
            if user_id:
                headers["X-Customer-ID"] = str(user_id)
                headers["X-User-ID"] = str(user_id)

        try:
            # If URL already has query string and skip_query_params is True, don't add params
            request_params = None if skip_query_params else request.query_params
            response = await client.request(
                method=request.method,
                url=target_url,
                params=request_params,
                content=body if body else None,
                headers=headers,
                follow_redirects=True
            )
        except httpx.ConnectError:
            raise HTTPException(status_code=502, detail="Backend service unavailable")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

        # Exclude hop-by-hop headers và CORS headers từ backend
        excluded_headers = {
            "content-length", "transfer-encoding", "connection", "keep-alive", 
            "proxy-authenticate", "proxy-authorization", "te", "trailers", "upgrade",
            "access-control-allow-origin", "access-control-allow-credentials",
            "access-control-allow-methods", "access-control-allow-headers",
            "access-control-expose-headers", "access-control-max-age"
        }
        
        # Lưu cookies trước khi filter
        cookies = response.headers.get_list("set-cookie") if "set-cookie" in response.headers else []
        
        # Filter headers
        response_headers = {
            k: v for k, v in response.headers.items() 
            if k.lower() not in excluded_headers and k.lower() != "set-cookie"
        }
        
        # Gateway thêm CORS headers
        origin = request.headers.get("origin", "*")
        response_headers["Access-Control-Allow-Origin"] = origin
        response_headers["Access-Control-Allow-Credentials"] = "true"
        response_headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response_headers["Access-Control-Allow-Headers"] = "content-type, authorization, cookie, x-user-id, x-customer-id"
        response_headers["Access-Control-Expose-Headers"] = "set-cookie"
        
        content_type = response.headers.get("content-type", "")
        if content_type and content_type.startswith("application/json"):
            try:
                json_response = JSONResponse(
                    content=response.json(), 
                    status_code=response.status_code, 
                    headers=response_headers
                )
            except:
                json_response = Response(
                    content=response.content, 
                    status_code=response.status_code, 
                    headers=response_headers, 
                    media_type=content_type
                )
        else:
            json_response = Response(
                content=response.content, 
                status_code=response.status_code, 
                headers=response_headers, 
                media_type=content_type
            )
        
        # Forward set-cookie headers
        for cookie in cookies:
            json_response.headers.append("set-cookie", cookie)
        
        return json_response

# ============================================
# AUTH SERVICE ROUTES
# ============================================

@router.post("/api/auth/login")
async def auth_login(request: Request):
    """Login endpoint"""
    url = f"{settings.auth_service_url}/api/auth/login"
    return await proxy_request(request, url)

@router.get("/api/auth/me")
async def auth_me(request: Request):
    """Get current user info"""
    url = f"{settings.customer_service_url}/api/customers/me"
    return await proxy_request(request, url)

@router.post("/api/auth/logout")
async def auth_logout(request: Request):
    """Logout endpoint"""
    url = f"{settings.auth_service_url}/api/auth/logout"
    return await proxy_request(request, url)

@router.post("/api/auth/verify-token")
async def auth_verify_token(request: Request):
    """Verify JWT token (internal)"""
    url = f"{settings.auth_service_url}/api/auth/verify-token"
    return await proxy_request(request, url, add_api_key=True)

# ============================================
# CUSTOMER SERVICE ROUTES
# ============================================

@router.get("/api/customers/me")
async def customer_me(request: Request):
    """Get current customer info"""
    url = f"{settings.customer_service_url}/api/customers/me"
    return await proxy_request(request, url)

@router.put("/api/customers/update-profile")
async def customer_update_profile(request: Request):
    """Update customer profile"""
    url = f"{settings.customer_service_url}/api/customers/update-profile"
    return await proxy_request(request, url)

# Alias cho frontend (frontend gọi /api/auth/profile thay vì /api/customers/update-profile)
@router.put("/api/auth/profile")
async def auth_update_profile(request: Request):
    """Update profile (alias)"""
    url = f"{settings.customer_service_url}/api/customers/update-profile"
    return await proxy_request(request, url)

# ============================================
# TUITION SERVICE ROUTES (Student Service)
# ============================================

@router.post("/api/students/search")
async def student_search(request: Request):
    """
    Search student by student_code
    Convert student_code to student_id for tuition service
    """
    def modify_body(data):
        # Tuition service expects student_id, but frontend sends student_code
        # In this system, student_code and student_id are the same
        if "student_code" in data:
            data["student_id"] = data.pop("student_code")
        return data
    
    url = f"{settings.tuition_service_url}/search"
    return await proxy_request(request, url, modify_body=modify_body)

@router.post("/api/tuitions/search")
async def tuition_search(request: Request):
    """Search student by student_id (alias)"""
    def modify_body(data):
        if "student_code" in data:
            data["student_id"] = data.pop("student_code")
        return data
    
    url = f"{settings.tuition_service_url}/search"
    return await proxy_request(request, url, modify_body=modify_body)

# ============================================
# PAYMENT SERVICE ROUTES
# ============================================

@router.post("/api/transactions/init")
async def payment_init(request: Request):
    """
    Initialize payment transaction (creates transaction and sends OTP)
    This endpoint maps to OTP issue endpoint
    Frontend sends: { student_code }
    """
    def modify_body(data):
        # Convert student_code to student_id for OTP service
        if "student_code" in data:
            data["student_id"] = data.pop("student_code")
        return data
    
    # Map to OTP issue endpoint
    url = f"{settings.otp_service_url}/api/otp/issue"
    return await proxy_request(request, url, modify_body=modify_body)

@router.post("/api/transactions/confirm")
async def payment_confirm(request: Request):
    """
    Confirm payment with OTP
    Frontend sends: { otp_code, student_id }
    """
    url = f"{settings.payment_service_url}/api/transactions/confirm"
    return await proxy_request(request, url)

@router.post("/api/transactions/{transaction_id}/confirm")
async def payment_confirm_with_id(request: Request, transaction_id: int):
    """
    Confirm payment with OTP (frontend sends transaction_id in path)
    Backend doesn't need transaction_id in path, it gets it from OTP verification
    So we just proxy to /confirm
    """
    url = f"{settings.payment_service_url}/api/transactions/confirm"
    return await proxy_request(request, url)

@router.get("/api/transactions/history")
async def payment_history(request: Request):
    """Get transaction history"""
    url = f"{settings.payment_service_url}/api/transactions/history"
    return await proxy_request(request, url)

@router.get("/api/transactions/{transaction_id}")
async def payment_detail(request: Request, transaction_id: int):
    """Get transaction detail"""
    url = f"{settings.payment_service_url}/api/transactions/{transaction_id}"
    return await proxy_request(request, url)

@router.post("/api/transactions/{transaction_id}/cancel")
async def payment_cancel(request: Request, transaction_id: int):
    """
    Cancel transaction (internal endpoint)
    Backend cancel endpoint expects transaction_id as query parameter
    """
    # Backend expects: POST /api/transactions/cancel?transaction_id=123
    url = f"{settings.payment_service_url}/api/transactions/cancel?transaction_id={transaction_id}"
    return await proxy_request(request, url, add_api_key=True, skip_query_params=True)

# ============================================
# OTP SERVICE ROUTES
# ============================================

@router.post("/api/otp/issue")
async def otp_issue(request: Request):
    """
    Issue OTP for payment
    Frontend sends: { student_id } or { student_code }
    """
    def modify_body(data):
        # Convert student_code to student_id if needed
        if "student_code" in data:
            data["student_id"] = data.pop("student_code")
        return data
    
    url = f"{settings.otp_service_url}/api/otp/issue"
    return await proxy_request(request, url, modify_body=modify_body)

@router.post("/api/otp/verify")
async def otp_verify(request: Request):
    """Verify OTP (internal)"""
    url = f"{settings.otp_service_url}/api/otp/verify"
    return await proxy_request(request, url, add_api_key=True)

# ============================================
# CATCH-ALL ROUTE (Fallback)
# ============================================

@router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def route_to_service_fallback(request: Request, path: str):
    """
    Fallback route cho các endpoint chưa được định nghĩa rõ ràng
    Routes requests đến đúng service dựa trên prefix
    """
    request_path = request.url.path

    # Xử lý OPTIONS (preflight) requests
    if request.method == "OPTIONS":
        requested_headers = request.headers.get("access-control-request-headers", "")
        if not requested_headers:
            requested_headers = "content-type, authorization, cookie, x-user-id, x-customer-id"
        
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                "Access-Control-Allow-Headers": requested_headers,
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "86400",
            }
        )

    # Route đến service dựa trên prefix
    for prefix, base_url in SERVICE_MAP.items():
        if request_path.startswith(prefix):
            # Các service có prefix trong router: giữ nguyên path
            # - Auth service: prefix /api/auth
            # - Customer service: prefix /api/customers
            # - Payment service: prefix /api/transactions
            # - OTP service: prefix /api/otp
            services_with_prefix = ["/api/auth", "/api/customers", "/api/transactions", "/api/otp"]
            
            if prefix in services_with_prefix:
                # Giữ nguyên toàn bộ path
                url = base_url.rstrip('/') + request_path
            else:
                # Tuition service: strip prefix và chỉ giữ phần còn lại
                # Ví dụ: /api/students/search -> /search
                path_without_prefix = request_path[len(prefix):]
                if not path_without_prefix:
                    path_without_prefix = "/"
                url = base_url.rstrip('/') + path_without_prefix
            
            return await proxy_request(request, url)
    
    raise HTTPException(status_code=404, detail=f"Route not found: {request_path}")
