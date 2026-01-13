# Auth Service

## Mô tả
Auth Service là service **STATELESS** - không có database, chỉ xử lý JWT token.

## Chức năng
- ✅ Tạo JWT token khi user login
- ✅ Verify JWT token cho API Gateway
- ✅ Xóa JWT token khi user logout
- ❌ KHÔNG có database
- ❌ KHÔNG lưu user data
- ❌ KHÔNG hash password (Customer Service làm việc này)

## Endpoints

### Public Endpoints
- `POST /api/auth/login` - Đăng nhập (gọi Customer Service để verify)
- `POST /api/auth/logout` - Đăng xuất (xóa cookie)

### Internal Endpoints (Requires API Key)
- `POST /api/auth/verify-token` - Verify JWT (chỉ API Gateway gọi)

## Environment Variables
```env
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24

CUSTOMER_SERVICE_URL=http://customer-service:8006
INTERNAL_API_KEY=your-internal-api-key-change-in-production

SERVICE_PORT=8001
```

## Cài đặt

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --port 8001
```

## Docker

```bash
# Build image
docker build -t auth-service .

# Run container
docker run -p 8001:8001 \
  -e JWT_SECRET_KEY=your-secret-key \
  -e CUSTOMER_SERVICE_URL=http://customer-service:8006 \
  -e INTERNAL_API_KEY=your-api-key \
  auth-service
```

## Architecture

```
┌──────────┐    POST /login       ┌─────────────┐
│ Frontend │ ──────────────────> │ Auth Service │
└──────────┘   (username, pass)   └─────────────┘
                                         │
                                         │ POST /search (verify)
                                         ▼
                                  ┌──────────────────┐
                                  │ Customer Service │
                                  │   (has database) │
                                  └──────────────────┘
                                         │
                                         │ Return user info
                                         ▼
                                  ┌─────────────┐
                                  │ Auth Service │
                                  │ Generate JWT │
                                  │ Set Cookie   │
                                  └─────────────┘
```

## Design Principles
- **Stateless:** Không lưu session, không có database
- **Single Responsibility:** Chỉ xử lý JWT, không biết gì về user data
- **Separation of Concerns:** Customer Service quản lý user data, Auth Service chỉ quản lý token
