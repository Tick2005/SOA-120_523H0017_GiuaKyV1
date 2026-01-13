import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "a8f5f167f44f4964e6c998dee827110c3e7b6e3c9c3f4f7e8a1b2c3d4e5f6a7b")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24  # 24 hours
    
    # Customer Service URL (internal)
    CUSTOMER_SERVICE_URL: str = os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8006")
    
    # Internal API Key (for service-to-service communication)
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x")
    
    # Cookie Settings
    COOKIE_NAME: str = "access_token"
    COOKIE_HTTPONLY: bool = True
    COOKIE_SECURE: bool = True  # Set to True in production with HTTPS
    COOKIE_SAMESITE: str = "strict"
    COOKIE_MAX_AGE: int = 86400  # 24 hours in seconds
    
    # Service Config
    SERVICE_NAME: str = "Auth Service"
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8001"))

settings = Settings()
