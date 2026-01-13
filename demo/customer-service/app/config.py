import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database Configuration
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "customer-db")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "rootpassword")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "customer_db")
    
    # Internal API Key (for service-to-service communication)
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x")
    
    # Service Config
    SERVICE_NAME: str = "Customer Service"
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8006"))
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

settings = Settings()
