from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import image_processing, auth
from app.database import engine
from app.models import models
import os
import logging
import time

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ghibli AI Backend",
    description="AI图片处理服务 - 可扩展的图像处理API，支持用户注册登录",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    try:
        # Log request details
        print(f"🔵 [REQUEST] {request.method} {request.url}")
        print(f"🔵 [HEADERS] {dict(request.headers)}")
        
        # For POST requests, try to log body (handle carefully)
        if request.method == "POST":
            try:
                body = await request.body()
                if len(body) < 1000:  # Only log small bodies
                    print(f"🔵 [BODY] {body.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"🔵 [BODY ERROR] {e}")
        
        # Process request
        response = await call_next(request)
        
        # Log response time
        process_time = time.time() - start_time
        print(f"🟢 [RESPONSE] Status: {response.status_code}, Time: {process_time:.3f}s")
        
        return response
    except Exception as e:
        # Log middleware errors
        process_time = time.time() - start_time
        print(f"🔴 [MIDDLEWARE ERROR] {str(e)}, Time: {process_time:.3f}s")
        # Re-raise exception for FastAPI's exception handler
        raise

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://lite-ai-web.vercel.app",
        "https://*.vercel.app",
        "http://22d9ec42059e446fb960e64c3dd6c7c3.ap-singapore.myide.io",
        "http://b924ede87fea4efca710303a2b948404.ap-singapore.myide.io",
        "*"  # Temporarily allow all origins for debugging
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(image_processing.router, prefix="/api", tags=["图片处理"])
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])

# Initialize storage system
upload_dir = "./uploads"
try:
    os.makedirs(upload_dir, exist_ok=True)
    # Set directory permissions to 755
    os.chmod(upload_dir, 0o755)
    print(f"✅ Upload directory ready: {upload_dir}")
except Exception as e:
    print(f"❌ Upload directory creation failed: {str(e)}")

# Add static file service for direct image access
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialization when application starts"""
    print("🚀 Ghibli AI Backend starting...")
    
    # Check upload directory status
    if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
        print(f"✅ Upload directory writable: {upload_dir}")
    else:
        print(f"⚠️ Upload directory permission issue: {upload_dir}")
    
    # Log filename handler status
    print("✅ Filename handler initialized")
    print("✅ Support for special characters and multilingual filenames")
    
    print("🎉 System startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when application shuts down"""
    print("👋 Ghibli AI Backend shutting down...")

@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return {}
    return {
        "message": "Ghibli AI Backend API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ghibli-ai-backend"}

# Add startup debug information
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    print(f"🔍 Health check available at: /api/health")
    uvicorn.run(app, host="0.0.0.0", port=port)