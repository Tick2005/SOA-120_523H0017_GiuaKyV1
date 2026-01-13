import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Lấy trực tiếp từ environment (Docker)
    auth_service_url: str = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    customer_service_url: str = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8006")
    tuition_service_url: str = os.getenv("TUITION_SERVICE_URL", "http://tuition-service:8002")
    payment_service_url: str = os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8003")
    otp_service_url: str = os.getenv("OTP_SERVICE_URL", "http://otp-service:8004")
    internal_api_key: str = os.getenv("INTERNAL_API_KEY", "sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x")

settings = Settings()
