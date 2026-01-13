# OTP Service

Microservice xử lý tạo và xác thực OTP cho thanh toán học phí.

## Chức năng

- Tạo OTP và gửi email (PUBLIC API)
- Xác thực OTP (INTERNAL API)
- Tự động expire OTP sau 5 phút

## API Endpoints

### PUBLIC APIs (Requires JWT)

- `POST /api/otp/issue` - Tạo OTP mới và gửi email

### INTERNAL APIs (Requires API Key)

- `POST /api/otp/verify` - Xác thực OTP

## Database Schema

```sql
CREATE TABLE otp (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    otp_code VARCHAR(6) NOT NULL,
    transaction_id BIGINT UNIQUE NOT NULL,
    status ENUM('active', 'used', 'expired') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Email Configuration

OTP Service sử dụng SMTP để gửi OTP email trực tiếp (không qua Mail Service).

## Environment Variables

- `SERVICE_PORT` - Port của service (default: 8004)
- `DATABASE_URL` - MySQL connection string
- `INTERNAL_API_KEY` - API key cho internal communication
- `PAYMENT_SERVICE_URL` - URL của Payment Service
- `CUSTOMER_SERVICE_URL` - URL của Customer Service
- `STUDENT_SERVICE_URL` - URL của Student Service
- `SMTP_HOST` - SMTP server host
- `SMTP_PORT` - SMTP server port
- `SMTP_USER` - SMTP username
- `SMTP_PASSWORD` - SMTP password
- `SMTP_FROM_EMAIL` - Sender email address
- `SMTP_FROM_NAME` - Sender name
- `OTP_EXPIRY_MINUTES` - OTP validity duration (default: 5)
- `OTP_LENGTH` - OTP code length (default: 6)

## Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## Docker

```bash
# Build image
docker build -t otp-service .

# Run container
docker run -p 8004:8004 otp-service
```
