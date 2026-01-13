import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@tuition_db:3306/tuition_db"
)

# Internal API Key for service-to-service communication
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "sk_live_51KxYz9H8mN2pQ3rS4tU5vW6xY7zA8bC9dE0fG1hI2jK3lM4nO5pQ6rS7tU8vW9x")

# Service info
SERVICE_NAME = "Tuition Service"
SERVICE_PORT = 8002
