# Customer Service

## Mô tả
Customer Service quản lý thông tin khách hàng và số dư tài khoản.

## Database
- **Database:** customer_db (MySQL)
- **Table:** customers
  - id (BIGINT, PK, AUTO_INCREMENT)
  - username (VARCHAR(50), UNIQUE, NOT NULL)
  - email (VARCHAR(100), UNIQUE, NOT NULL)
  - password (VARCHAR(255), NOT NULL) - Plain text
  - balance (DECIMAL(15,2), DEFAULT 0)

## Endpoints

### Public Endpoints
- `GET /api/customers/me` - Lấy thông tin customer hiện tại

### Internal Endpoints (Requires API Key)
- `POST /api/customers/search` - Tìm customer theo username/password
- `POST /api/customers/deduct-balance` - Trừ tiền từ tài khoản

## Environment Variables
```env
MYSQL_HOST=customer-db
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=rootpassword
MYSQL_DATABASE=customer_db

INTERNAL_API_KEY=your-internal-api-key-change-in-production
SERVICE_PORT=8006
```

## Cài đặt

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --reload --port 8006
```

## Docker

```bash
# Build image
docker build -t customer-service .

# Run container
docker run -p 8006:8006 \
  -e MYSQL_HOST=customer-db \
  -e MYSQL_PASSWORD=rootpassword \
  -e INTERNAL_API_KEY=your-api-key \
  customer-service
```

## Sample Data
File `init.sql` chứa sample data:
- user123 / password123 (balance: 10M)
- john_doe / john1234 (balance: 5M)
- jane_smith / jane1234 (balance: 15M)
- admin / admin123 (balance: 50M)

## API Examples

### GET /api/customers/me
```bash
curl -X GET http://localhost:8006/api/customers/me \
  -H "X-Customer-ID: 1" \
  -H "Cookie: access_token=xxx"
```

### POST /api/customers/search (Internal)
```bash
curl -X POST http://localhost:8006/api/customers/search \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "password123"}'
```

### POST /api/customers/deduct-balance (Internal)
```bash
curl -X POST http://localhost:8006/api/customers/deduct-balance \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "amount": 1000000,
    "transaction_code": "TXN20251107001"
  }'
```
