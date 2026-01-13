from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routes import router
from app.middleware import auth_middleware
import os

app = FastAPI(
    title="iBanking TDTU - API Gateway",
    version="2.0",
    docs_url="/docs"
)

# Auth middleware để kiểm tra token
app.middleware("http")(auth_middleware)

# UI folder được mount từ docker-compose tại /ui
ui_dir = "/ui"

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "api-gateway"}

# Serve HTML files (phải khai báo TRƯỚC api router)
if os.path.exists(ui_dir):
    @app.get("/")
    async def read_index():
        return FileResponse(f"{ui_dir}/index.html")
    
    @app.get("/payment.html")
    async def read_payment():
        return FileResponse(f"{ui_dir}/payment.html")
    
    @app.get("/profile.html")
    async def read_profile():
        return FileResponse(f"{ui_dir}/profile.html")
    
    @app.get("/transactions.html")
    async def read_transactions():
        return FileResponse(f"{ui_dir}/transactions.html")
    
    @app.get("/otp.html")
    async def read_otp():
        return FileResponse(f"{ui_dir}/otp.html")
    
    @app.get("/success.html")
    async def read_success():
        return FileResponse(f"{ui_dir}/success.html")
    
    @app.get("/header.html")
    async def read_header():
        return FileResponse(f"{ui_dir}/header.html")
    
    @app.get("/footer.html")
    async def read_footer():
        return FileResponse(f"{ui_dir}/footer.html")
    
    @app.get("/favicon.ico")
    async def read_favicon():
        # Trả về logo làm favicon nếu chưa có file .ico riêng
        logo_path = f"{ui_dir}/img/Logo-TDTU.png"
        if os.path.exists(logo_path):
            return FileResponse(logo_path, media_type="image/png")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Favicon not found")

# Include API router SAU (để catch-all pattern không ăn mất static routes)
app.include_router(router)

# Mount static assets CUỐI CÙNG
if os.path.exists(ui_dir):
    if os.path.exists(f"{ui_dir}/css"):
        app.mount("/css", StaticFiles(directory=f"{ui_dir}/css"), name="css")
    if os.path.exists(f"{ui_dir}/js"):
        app.mount("/js", StaticFiles(directory=f"{ui_dir}/js"), name="js")
    if os.path.exists(f"{ui_dir}/img"):
        app.mount("/img", StaticFiles(directory=f"{ui_dir}/img"), name="img")
