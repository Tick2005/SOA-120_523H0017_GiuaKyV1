from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import SERVICE_NAME, SERVICE_PORT
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=SERVICE_NAME,
    description="Payment Service - Handle payment transactions with sequential payment logic",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.get("/")
def read_root():
    return {
        "service": SERVICE_NAME,
        "status": "running",
        "port": SERVICE_PORT,
        "version": "2.1.0",
        "description": "Handle payment transactions for tuition fees",
        "endpoints": [
            "POST /api/transactions/create (INTERNAL - OTP Service)",
            "POST /api/transactions/confirm (PUBLIC - Frontend)",
            "POST /api/transactions/cancel (INTERNAL - OTP Service)",
            "GET /api/transactions/history (PUBLIC - Frontend)"
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": SERVICE_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
