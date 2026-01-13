import os
from dotenv import load_dotenv

load_dotenv()

# Service Configuration
SERVICE_NAME = "OTP Service"
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8004))

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:rootpassword@localhost:3306/otp_db"
)

# Internal API Key for service-to-service communication
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x")

# Service URLs
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://localhost:8003")
CUSTOMER_SERVICE_URL = os.getenv("CUSTOMER_SERVICE_URL", "http://localhost:8006")
STUDENT_SERVICE_URL = os.getenv("STUDENT_SERVICE_URL", "http://localhost:8002")

# Email Configuration (SMTP)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "soagk1tdtu@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "wveg zevy kdya rxbv")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "soagk1tdtu@gmail.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "iBanking TDTU")

# OTP Configuration
OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", 5))
OTP_LENGTH = int(os.getenv("OTP_LENGTH", 6))
