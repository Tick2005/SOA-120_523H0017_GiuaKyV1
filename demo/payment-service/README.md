# Payment Service

Microservice xử lý thanh toán học phí với logic thanh toán tuần tự.

## Chức năng

- Tạo transaction thanh toán (INTERNAL API)
- Xác nhận thanh toán với OTP (PUBLIC API)
- Hủy transaction khi OTP expired (INTERNAL API)
- Lấy lịch sử giao dịch (PUBLIC API)

## API Endpoints

### INTERNAL APIs (Requires API Key)

- `POST /api/transactions/create` - Tạo transaction mới
- `POST /api/transactions/cancel` - Hủy transaction

### PUBLIC APIs (Requires JWT)

- `POST /api/transactions/confirm` - Xác nhận thanh toán với OTP
- `GET /api/transactions/history` - Lấy lịch sử giao dịch

## Database Schema

```sql
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    tuition_id BIGINT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

- `SERVICE_PORT` - Port của service (default: 8003)
- `DATABASE_URL` - MySQL connection string
- `INTERNAL_API_KEY` - API key cho internal communication
- `CUSTOMER_SERVICE_URL` - URL của Customer Service
- `STUDENT_SERVICE_URL` - URL của Student Service
- `MAIL_SERVICE_URL` - URL của Mail Service

## Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

## Docker

```bash
# Build image
docker build -t payment-service .

# Run container
docker run -p 8003:8003 payment-service
```
