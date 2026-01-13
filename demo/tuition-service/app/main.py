from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
from .database import engine, Base
from .config import SERVICE_NAME, SERVICE_PORT

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=SERVICE_NAME,
    description="Tuition Service - Manage student tuitions with sequential payment logic",
    version="2.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="", tags=["tuitions"])

@app.get("/")
def read_root():
    return {
        "service": SERVICE_NAME,
        "status": "running",
        "port": SERVICE_PORT,
        "version": "2.1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
