from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .config import SERVICE_NAME, SERVICE_PORT
from .database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=SERVICE_NAME,
    description="OTP Service - Handle OTP generation and verification for payment confirmation",
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
        "description": "Handle OTP generation and verification",
        "endpoints": [
            "POST /api/otp/issue (PUBLIC - Frontend)",
            "POST /api/otp/verify (INTERNAL - Payment Service)"
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
