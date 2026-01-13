# 🏦 iBanking TDTU - Tuition Payment System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern **microservices-based** online banking system for Ton Duc Thang University students to pay tuition fees with **OTP verification** and **sequential payment logic**.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Database Schema](#-database-schema)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Troubleshooting](#-troubleshooting)
- [Contributors](#-contributors)

---

## 🌟 Overview

**iBanking TDTU** is a full-stack web application that allows university students to:
- **Search** their tuition fees by student ID
- **View** all unpaid tuition fees in chronological order
- **Pay** tuition fees sequentially (oldest first) using OTP verification
- **Track** transaction history with email receipts

The system enforces **sequential payment logic**: students must pay tuition fees in order (by semester and academic year) and cannot skip older fees.

---

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication with **HttpOnly cookies**
- 24-hour token expiration with automatic refresh
- Secure password hashing with bcrypt
- Role-based access control (customer vs internal APIs)

### 💳 Payment Processing
- **Sequential payment logic**: Only the oldest unpaid tuition can be paid (`canPay` flag)
- **OTP verification** via email (5-minute expiration)
- **Transaction locking** to prevent race conditions
- Automatic balance checking and deduction
- Email invoices sent asynchronously

### 🎓 Tuition Management
- Search tuition fees by student code
- View all tuition fees with payment status
- Automatic tuition status update after payment
- Multi-semester and multi-year support

### 📊 Transaction History
- View all completed and pending transactions
- Real-time balance updates
- Transaction timestamps and status tracking

### 🎨 User Interface
- Modern, responsive design with Bootstrap 5
- Real-time form validation
- Loading states and error handling
- Mobile-friendly interface

---

## 🏗️ Architecture

### Microservices Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                          │
│                       (Port 8000)                           │
│  - Authentication Middleware                                │
│  - Request Routing                                          │
│  - X-Customer-ID Injection                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────┬─────────┬─────────┐
        │         │         │         │         │         │
        ▼         ▼         ▼         ▼         ▼         ▼
    ┌───────┐ ┌────────┐ ┌───────┐ ┌────────┐ ┌───────┐ ┌────────┐
    │ Auth  │ │Customer│ │Tuition│ │Payment │ │  OTP  │ │   UI   │
    │Service│ │Service │ │Service│ │Service │ │Service│ │ Static │
    │:8001  │ │:8006   │ │:8002  │ │:8003   │ │:8004  │ │ Files  │
    └───┬───┘ └───┬────┘ └───┬───┘ └───┬────┘ └───┬───┘ └────────┘
        │         │           │         │         │
        │    ┌────▼────┐ ┌───▼────┐ ┌──▼─────┐ ┌─▼──────┐
        │    │Customer │ │Tuition │ │Payment │ │  OTP   │
        │    │   DB    │ │   DB   │ │   DB   │ │   DB   │
        │    │ :3307   │ │ :3308  │ │ :3309  │ │ :3310  │
        │    └─────────┘ └────────┘ └────────┘ └────────┘
        │
        └──────► Stateless (No Database)
```

### Service Communication

```
Frontend → API Gateway → Auth Service → Customer Service (verify credentials)
                       ↓
                     Tuition Service (search fees)
                       ↓
                     OTP Service → Payment Service (create transaction)
                                 → Email Service (send OTP)
                       ↓
                     Payment Service → OTP Service (verify OTP)
                                     → Customer Service (deduct balance)
                                     → Tuition Service (mark paid)
                                     → Email Service (send invoice)
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.11
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic 2.x
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **HTTP Client**: httpx (for inter-service communication)

### Database
- **DBMS**: MySQL 8.0
- **Databases**: 4 separate databases (customer, tuition, payment, otp)
- **Connection Pooling**: SQLAlchemy engine with pool_pre_ping

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript
- **UI Framework**: Bootstrap 5.3
- **Icons**: Bootstrap Icons
- **HTTP Client**: Fetch API with async/await

### DevOps
- **Containerization**: Docker & Docker Compose 3.9
- **Networking**: Bridge network with service discovery
- **Volumes**: Persistent MySQL data volumes
- **Health Checks**: Container health monitoring

---

## 📦 Prerequisites

Before running this project, ensure you have:

- **Docker Desktop** 4.x or higher ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose** 2.x or higher (included with Docker Desktop)
- **8GB RAM** minimum (recommended for running 10 containers)
- **Ports available**: 8000-8006, 3307-3310

**Optional** (for development):
- Python 3.11+
- Node.js 18+ (for frontend tooling)
- MySQL Workbench (for database inspection)

---

## 🚀 Installation

### 1. Clone the code 

You download ỉt and moving open the code in vscode.
Moving powersehell to demo to install for all to ready to starting practice.
```bash
    cd demo
```

### 2. Project Structure Verification

```bash
demo/
├── api-gateway/           # API Gateway service
├── auth-service/          # Authentication service
├── customer-service/      # Customer management service
├── tuition-service/       # Tuition management service
├── payment-service/       # Payment processing service
├── otp-service/          # OTP generation & verification service
├── ui/                   # Frontend static files
├── docker-compose.yml    # Docker orchestration
└── README.md            # This file
```

### 3. Environment Configuration (Optional)

All services use environment variables defined in `docker-compose.yml`. You can modify them if needed:

```yaml
# Key environment variables:
JWT_SECRET_KEY: a8f5f167f44f4964e6c998dee827110c3e7b6e3c9c3f4f7e8a1b2c3d4e5f6a7b
INTERNAL_API_KEY: sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x
ACCESS_TOKEN_EXPIRE_HOURS: 24
```

### 4. Start the Application

```bash
# Start all services (detached mode)
docker compose up -d

# Check container status
docker compose ps

# View logs (all services)
docker compose logs -f

# View logs (specific service)
docker compose logs -f api-gateway
```

### 5. Wait for Services to Be Ready

All services have health checks. Wait until all containers show `healthy` status:

```bash
docker compose ps
```

Expected output:
```
NAME               STATUS                    PORTS
api-gateway        Up (healthy)             0.0.0.0:8000->8000/tcp
auth-service       Up (healthy)             0.0.0.0:8001->8001/tcp
customer-service   Up (healthy)             0.0.0.0:8006->8006/tcp
tuition-service    Up (healthy)             0.0.0.0:8002->8002/tcp
payment-service    Up (healthy)             0.0.0.0:8003->8003/tcp
otp-service        Up (healthy)             0.0.0.0:8004->8004/tcp
customer-db        Up (healthy)             0.0.0.0:3307->3306/tcp
tuition-db         Up (healthy)             0.0.0.0:3308->3306/tcp
payment-db         Up (healthy)             0.0.0.0:3309->3306/tcp
otp-db             Up (healthy)             0.0.0.0:3310->3306/tcp
```

---

## 💻 Usage

### Access the Application

**Frontend URL**: http://localhost:8000

**API Gateway**: http://localhost:8000/docs (Swagger UI)

**Individual Service Docs**:
- Auth Service: http://localhost:8001/docs
- Customer Service: http://localhost:8006/docs
- Tuition Service: http://localhost:8002/docs
- Payment Service: http://localhost:8003/docs
- OTP Service: http://localhost:8004/docs

### Default Test Accounts

| Username | Password | Email | Balance |
|----------|----------|-------|---------|
| user123 | password123 | phanvanduong1223456@gmail.com | 10,000,000 VND |
| john_doe | john1234 | phanduong19032023@gmail.com | 5,000,000 VND |
| jane_smith | jane1234 | jane@example.com | 15,000,000 VND |
| admin | admin123 | khangtrongclone@gmail.com | 50,000,000 VND |

### Test Student IDs

| Student ID | Name | Unpaid Tuitions | Total Amount |
|------------|------|-----------------|--------------|
| 52000123 | Nguyen Van A | 3 semesters | 15,500,000 VND |
| 520H0696 | Tran Thi B | 2 semesters | 10,000,000 VND |

### Complete Payment Flow

1. **Login**
   - Navigate to http://localhost:8000
   - Enter username: `user123`, password: `password123`
   - JWT token stored in HttpOnly cookie (24 hours)

2. **Search Tuition**
   - Click "Payment" menu
   - Enter student code: `52000123`
   - View all tuition fees (only oldest unpaid has `canPay: true`)

3. **Initialize Payment**
   - Click "Pay Now" button on the oldest unpaid tuition
   - System creates transaction and sends OTP to email
   - Check email for 6-digit OTP code (expires in 5 minutes)

4. **Confirm Payment**
   - Enter OTP code in the confirmation page
   - System verifies OTP, checks balance, deducts money
   - Transaction status changes to "completed"
   - Invoice email sent automatically

5. **View History**
   - Navigate to "Transactions" menu
   - View all completed and pending transactions

---

## 📚 API Documentation

### Public APIs (via API Gateway)

All public APIs should go through API Gateway (port 8000). Authentication is automatic via JWT cookie.

#### Authentication

**POST /api/auth/login**
```json
Request:
{
  "username": "user123",
  "password": "password123"
}

Response (200 OK):
{
  "user": {
    "id": 1,
    "username": "user123",
    "email": "phanvanduong1223456@gmail.com",
    "balance": 10000000
  }
}
// JWT token set in HttpOnly cookie
```

**POST /api/auth/logout**
```json
Response (200 OK):
{
  "message": "Logged out successfully"
}
```

#### Customer Profile

**GET /api/customers/me**
```json
Response (200 OK):
{
  "id": 1,
  "username": "user123",
  "email": "phanvanduong1223456@gmail.com",
  "full_name": "Nguyen Van User",
  "phone_number": "0901234567",
  "balance": 5000000.00
}
```

**PUT /api/customers/update-profile**
```json
Request (all fields optional):
{
  "username": "newusername",
  "email": "newemail@example.com",
  "full_name": "New Name",
  "phone_number": "0987654321",
  "current_password": "password123",
  "new_password": "newpassword123"
}

Response (200 OK):
{
  "success": true,
  "message": "Profile updated successfully",
  "user": { ... }
}
```

#### Tuition Search

**POST /api/students/search**
```json
Request:
{
  "student_code": "52000123"
}

Response (200 OK):
{
  "student": {
    "student_id": "52000123",
    "student_name": "Nguyen Van A",
    "student_email": "52000123@student.tdtu.edu.vn"
  },
  "all_tuitions": [
    {
      "id": 1,
      "semester": 2,
      "academic_year": "2023-2024",
      "fee": 0,
      "status": "paid",
      "canPay": false
    },
    {
      "id": 2,
      "semester": 1,
      "academic_year": "2024-2025",
      "fee": 5000000.00,
      "status": "unpaid",
      "canPay": true  // Only this can be paid
    },
    {
      "id": 3,
      "semester": 2,
      "academic_year": "2024-2025",
      "fee": 5000000.00,
      "status": "unpaid",
      "canPay": false  // Must pay previous first
    }
  ]
}
```

#### Payment Transaction

**POST /api/transactions/init**
```json
Request:
{
  "student_code": "52000123"
}

Response (200 OK):
{
  "success": true,
  "transaction_id": 1,
  "tuition_info": {
    "id": 2,
    "semester": 1,
    "academic_year": "2024-2025",
    "amount": 5000000.00
  },
  "message": "OTP has been sent via email. Please check your inbox.",
  "expires_in_minutes": 5
}
```

**POST /api/transactions/confirm**
```json
Request:
{
  "otp_code": "123456",
  "student_id": "52000123"
}

Response (200 OK):
{
  "success": true,
  "message": "Payment successful",
  "transaction": {
    "id": 1,
    "customer_id": 1,
    "tuition_id": 2,
    "amount": 5000000.00,
    "status": "completed",
    "created_at": "2025-11-09T10:30:00"
  },
  "new_balance": 5000000.00
}

Error Response (400 Bad Request):
{
  "detail": "OTP is invalid or expired"
}

Error Response (400 Bad Request):
{
  "detail": "Insufficient balance. Current: 1,000,000 VND, Required: 5,000,000 VND"
}
```

**GET /api/transactions/history**
```json
Response (200 OK):
{
  "transactions": [
    {
      "id": 1,
      "customer_id": 1,
      "tuition_id": 2,
      "amount": 5000000.00,
      "status": "completed",
      "created_at": "2025-11-09T10:30:00"
    }
  ]
}
```

### Internal APIs (Inter-Service Communication)

Internal APIs require `X-API-Key` header. Not accessible from frontend.

**Payment Service → Tuition Service**
```
POST /get-payable
Header: X-API-Key: sk_live_51...
```

**Payment Service → Customer Service**
```
POST /api/customers/deduct-balance
Header: X-API-Key: sk_live_51...
```

**OTP Service → Payment Service**
```
POST /api/transactions/create
Header: X-API-Key: sk_live_51...
```

For complete API documentation, see [API_TESTING_GUIDE.md](./API_TESTING_GUIDE.md)

---

## 🗄️ Database Schema

### Customer Database (customer_db)

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0,
    INDEX idx_username (username),
    INDEX idx_email (email)
);
```

### Tuition Database (tuition_db)

```sql
CREATE TABLE tuitions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    student_id VARCHAR(20) NOT NULL,
    student_name VARCHAR(100) NOT NULL,
    student_email VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    fee DECIMAL(15,2) NOT NULL,
    status ENUM('unpaid', 'paid') DEFAULT 'unpaid',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_student_id (student_id),
    INDEX idx_student_year_semester (student_id, academic_year, semester)
);
```

### Payment Database (payment_db)

```sql
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    tuition_id BIGINT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id),
    INDEX idx_status (status)
);
```

### OTP Database (otp_db)

```sql
CREATE TABLE otps (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    transaction_id BIGINT NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_otp_code (otp_code),
    INDEX idx_transaction_id (transaction_id)
);
```

---

## 🧪 Testing

### Manual Testing with Browser

1. Open http://localhost:8000
2. Login with test account
3. Search student tuition
4. Initiate payment
5. Check email for OTP
6. Confirm payment
7. View transaction history

### API Testing with Postman

Import the Postman collection: [postman-test.json](./postman-test.json)

**Test Sequence:**
1. Login → Get JWT cookie
2. Search tuition → Get tuition list
3. Init payment → Get transaction_id and OTP email
4. Confirm payment → Complete transaction
5. View history → Verify transaction

### API Testing with Swagger UI

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Get JWT token from browser console:
   ```javascript
   document.cookie.split('; ')
     .find(row => row.startsWith('access_token='))
     .split('=')[1]
   ```
4. Paste token into authorization
5. Test endpoints

### Database Testing

**Connect to MySQL:**
```bash
# Customer DB
mysql -h 127.0.0.1 -P 3307 -u customer_user -p customer_db
# Password: customer_pass

# Tuition DB
mysql -h 127.0.0.1 -P 3308 -u tuition_user -p tuition_db
# Password: tuition_pass

# Payment DB
mysql -h 127.0.0.1 -P 3309 -u payment_user -p payment_db
# Password: payment_pass

# OTP DB
mysql -h 127.0.0.1 -P 3310 -u otp_user -p otp_db
# Password: otp_pass
```

**Test Queries:**
```sql
-- Check customer balance
SELECT id, username, balance FROM customers WHERE username = 'user123';

-- Check unpaid tuitions
SELECT * FROM tuitions WHERE student_id = '52000123' AND status = 'unpaid'
ORDER BY academic_year ASC, semester ASC;

-- Check transactions
SELECT * FROM transactions WHERE customer_id = 1 ORDER BY created_at DESC;

-- Check OTP codes
SELECT * FROM otps WHERE customer_id = 1 AND is_used = 0 
AND expires_at > NOW() ORDER BY created_at DESC;
```

---

## 📁 Project Structure

```
demo/
├── api-gateway/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── config.py            # Service URLs
│       ├── middleware.py        # JWT verification
│       └── routes.py            # Request routing
│
├── auth-service/
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── config.py            # JWT settings
│       ├── auth.py              # JWT utilities
│       ├── routes.py            # Auth endpoints
│       └── schemas.py           # Pydantic models
│
├── customer-service/
│   ├── Dockerfile
│   ├── init.sql                 # Database schema + seed data
│   ├── README.md
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── config.py            # DB connection
│       ├── database.py          # SQLAlchemy setup
│       ├── models.py            # Customer model
│       ├── routes.py            # Customer endpoints
│       └── schemas.py           # Pydantic models
│
├── tuition-service/
│   ├── Dockerfile
│   ├── init.sql                 # Database schema + seed data
│   ├── README.md
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── config.py            # DB connection
│       ├── database.py          # SQLAlchemy setup
│       ├── models.py            # Tuition model
│       ├── routes.py            # Tuition endpoints
│       └── schemas.py           # Pydantic models
│
├── payment-service/
│   ├── Dockerfile
│   ├── init.sql                 # Database schema
│   ├── README.md
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── config.py            # DB + service URLs
│       ├── database.py          # SQLAlchemy setup
│       ├── models.py            # Transaction model
│       ├── routes.py            # Payment endpoints
│       ├── schemas.py           # Pydantic models
│       └── email_utils.py       # Email sending (SMTP)
│
├── otp-service/
│   ├── Dockerfile
│   ├── init.sql                 # Database schema
│   ├── README.md
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI app
│       ├── config.py            # DB + SMTP settings
│       ├── database.py          # SQLAlchemy setup
│       ├── models.py            # OTP model
│       ├── routes.py            # OTP endpoints
│       ├── schemas.py           # Pydantic models
│       └── utils.py             # OTP generation + email
│
├── ui/
│   ├── index.html               # Login page
│   ├── payment.html             # Tuition search & payment
│   ├── otp.html                 # OTP input page
│   ├── success.html             # Payment success page
│   ├── profile.html             # User profile page
│   ├── transactions.html        # Transaction history
│   ├── css/
│   │   └── style.css            # Custom styles
│   └── js/
│       ├── api.js               # API helper functions
│       ├── auth-check.js        # Authentication check
│       ├── login.js             # Login logic
│       ├── logout.js            # Logout logic
│       ├── payment.js           # Payment logic
│       ├── otp.js               # OTP verification
│       ├── profile.js           # Profile management
│       ├── transactions.js      # Transaction history
│       └── success.js           # Success page logic
│
├── docker-compose.yml           # Container orchestration
├── API_TESTING_GUIDE.md         # API testing documentation
├── MICROSERVICES_ARCHITECTURE.md # Architecture documentation
├── postman-test.json            # Postman collection
└── README.md                    # This file
```

---

## ⚙️ Environment Variables

### API Gateway
```env
AUTH_SERVICE_URL=http://auth-service:8001
CUSTOMER_SERVICE_URL=http://customer-service:8006
TUITION_SERVICE_URL=http://tuition-service:8002
PAYMENT_SERVICE_URL=http://payment-service:8003
OTP_SERVICE_URL=http://otp-service:8004
INTERNAL_API_KEY=sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x
```

### Auth Service
```env
JWT_SECRET_KEY=a8f5f167f44f4964e6c998dee827110c3e7b6e3c9c3f4f7e8a1b2c3d4e5f6a7b
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_HOURS=24
CUSTOMER_SERVICE_URL=http://customer-service:8006
INTERNAL_API_KEY=sk_live_51...
```

### Customer Service
```env
MYSQL_HOST=customer-db
MYSQL_PORT=3306
MYSQL_USER=customer_user
MYSQL_PASSWORD=customer_pass
MYSQL_DATABASE=customer_db
INTERNAL_API_KEY=sk_live_51...
```

### Payment Service
```env
MYSQL_HOST=payment-db
MYSQL_PORT=3306
MYSQL_USER=payment_user
MYSQL_PASSWORD=payment_pass
MYSQL_DATABASE=payment_db
CUSTOMER_SERVICE_URL=http://customer-service:8006
TUITION_SERVICE_URL=http://tuition-service:8002
OTP_SERVICE_URL=http://otp-service:8004
INTERNAL_API_KEY=sk_live_51...

# Email settings (for invoice)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@ibanking-tdtu.edu.vn
```

### OTP Service
```env
MYSQL_HOST=otp-db
MYSQL_PORT=3306
MYSQL_USER=otp_user
MYSQL_PASSWORD=otp_pass
MYSQL_DATABASE=otp_db
PAYMENT_SERVICE_URL=http://payment-service:8003
INTERNAL_API_KEY=sk_live_51...

# Email settings (for OTP)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "soagk1tdtu@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "...")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "soagk1tdtu@gmail.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "iBanking TDTU")
```

**Note**: Replace `your-email@gmail.com` and `your-app-password` with actual Gmail credentials. Generate app password from [Google Account Settings](https://myaccount.google.com/apppasswords).

---

## 🔧 Troubleshooting

### Container Issues

**Problem**: Containers not starting
```bash
# Check logs
docker compose logs

# Restart specific service
docker compose restart api-gateway

# Rebuild and restart
docker compose up -d --build api-gateway
```

**Problem**: Database connection refused
```bash
# Check database health
docker compose ps

# Wait for databases to be healthy
docker compose up -d
docker compose logs customer-db tuition-db payment-db otp-db

# Restart service after DB is ready
docker compose restart customer-service
```

### Port Conflicts

**Problem**: Port already in use
```bash
# Check what's using the port (Windows)
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <process_id> /F

# Or change ports in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead of 8000
```

### API Issues

**Problem**: 401 Unauthorized on API calls
- **Solution**: JWT token expired (24 hours). Login again.
- Check cookie in browser DevTools → Application → Cookies

**Problem**: 502 Bad Gateway
- **Solution**: Backend service not ready. Check service health:
```bash
docker compose ps
docker compose logs <service-name>
```

**Problem**: OTP not received
- **Solution**: Check email configuration in docker-compose.yml
- Verify SMTP credentials are correct
- Check spam folder
- View OTP service logs: `docker compose logs otp-service`

**Problem**: "Insufficient balance" error
- **Solution**: Check customer balance in database:
```bash
mysql -h 127.0.0.1 -P 3307 -u customer_user -pcustomer_pass customer_db
SELECT username, balance FROM customers;
```
- Update balance manually if needed:
```sql
UPDATE customers SET balance = 20000000 WHERE username = 'user123';
```

### Database Issues

**Problem**: Tables not created
```bash
# Check init.sql was executed
docker compose logs customer-db | grep "init.sql"

# Recreate database
docker compose down -v  # Remove volumes
docker compose up -d    # Recreate with fresh data
```

**Problem**: Connection timeout
- **Solution**: Increase health check retries in docker-compose.yml
```yaml
healthcheck:
  retries: 10  # Increase from 5
  interval: 15s  # Increase from 10s
```

### Email Issues

**Problem**: Gmail blocking SMTP
- **Solution**: Enable "Less secure app access" or use App Password
- Generate App Password: https://myaccount.google.com/apppasswords
- Update SMTP_PASSWORD in docker-compose.yml

**Problem**: Email sending slow
- **Solution**: Email is sent asynchronously (fire-and-forget)
- Check logs: `docker compose logs payment-service otp-service`

---

## 🤝 Contributors

| Name | Student ID | Email |
|------|-----------|-------|------|
| Nguyễn Đức Anh | 523H0002 | 523H0002@student.tdtu.edu.vn 
| Phan Văn Dương | 523H0017 | 523H0017@student.tdtu.edu.vn 
| Trần Đức Huy | 523H0033 | 523H0033@student.tdtu.edu.vn 

**Supervisor**: [Your Supervisor Name]

**Institution**: Ton Duc Thang University

**Course**: Service-Oriented Architecture (SOA)

**Academic Year**: 2024-2025

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [SQLAlchemy](https://www.sqlalchemy.org) - SQL toolkit and ORM
- [Docker](https://www.docker.com) - Containerization platform
- [Bootstrap](https://getbootstrap.com) - Frontend framework
- Ton Duc Thang University for project support

---

## 📞 Support

For questions or issues:
- Create an issue in this repository
- Email: [523H0002@student.tdtu.edu.vn][523H0017@student.tdtu.edu.vn][523H0033@student.tdtu.edu.vn]
- Slack: [Your Slack Channel]

---

## 🚀 Future Enhancements

- [ ] Add Redis caching for tuition search
- [ ] Implement rate limiting for API endpoints
- [ ] Add Prometheus + Grafana monitoring
- [ ] Deploy to Kubernetes
- [ ] Add CI/CD pipeline (GitHub Actions)
- [ ] Implement WebSocket for real-time notifications
- [ ] Add multi-language support (Vietnamese/English)
- [ ] Implement mobile app (React Native)
- [ ] Add payment history export (PDF/Excel)
- [ ] Implement refund functionality

---

**⭐ If you find this project helpful, please give it a star!**

**Made with ❤️ by TDTU Students**
