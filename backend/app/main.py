  from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import image_processing, auth
from app.database import engine
from app.models import models
import os

# 创建所有数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ghibli AI Backend",
    description="AI图片处理服务 - 可扩展的图像处理API，支持用户注册登录",
    version="1.0.0"
)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    
    try:
        # 记录请求详情
        print(f"🔵 [REQUEST] {request.method} {request.url}")
        print(f"🔵 [HEADERS] {dict(request.headers)}")
        
        # 如果是POST请求，尝试记录body（小心处理）
        if request.method == "POST":
            try:
                body = await request.body()
                if len(body) < 1000:  # 只记录小的body
                    print(f"🔵 [BODY] {body.decode('utf-8', errors='ignore')}")
            except Exception as e:
                print(f"🔵 [BODY ERROR] {e}")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应时间
        process_time = time.time() - start_time
        print(f"🟢 [RESPONSE] Status: {response.status_code}, Time: {process_time:.3f}s")
        
        return response
    except Exception as e:
        # 记录中间件错误
        process_time = time.time() - start_time
        print(f"🔴 [MIDDLEWARE ERROR] {str(e)}, Time: {process_time:.3f}s")
        # 重新抛出异常，让FastAPI的异常处理器处理
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://lite-ai-web.vercel.app",
        "https://*.vercel.app",
        "http://22d9ec42059e446fb960e64c3dd6c7c3.ap-singapore.myide.io",
        "http://b924ede87fea4efca710303a2b948404.ap-singapore.myide.io",
        "*"  # 临时允许所有域名用于调试
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_processing.router, prefix="/api", tags=["图片处理"])
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])

# 初始化存储系统
from app.utils.filename_handler import filename_handler
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建上传目录并设置权限
upload_dir = "./uploads"
try:
    os.makedirs(upload_dir, exist_ok=True)
    # 设置目录权限为755
    os.chmod(upload_dir, 0o755)
    print(f"✅ 上传目录已准备就绪: {upload_dir}")
except Exception as e:
    print(f"❌ 上传目录创建失败: {str(e)}")

# 添加静态文件服务，用于直接访问图片
# 注意：这里使用 /api/uploads 路径，但在路由中我们使用 /api/files
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

# 添加启动事件处理
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    print("🚀 Ghibli AI Backend 启动中...")
    
    # 检查上传目录状态
    if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
        print(f"✅ 上传目录可写: {upload_dir}")
    else:
        print(f"⚠️ 上传目录权限问题: {upload_dir}")
    
    # 记录文件名处理器状态
    print("✅ 文件名处理器已初始化")
    print("✅ 支持特殊字符和多语言文件名")
    
    print("🎉 系统启动完成!")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    print("👋 Ghibli AI Backend 正在关闭...")

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

# 添加启动时的调试信息
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting server on port {port}")
    print(f"🔍 Health check available at: /api/health")
    uvicorn.run(app, host="0.0.0.0", port=port)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import image_processing, auth
from app.database import engine
from app.models import models
import os

# 创建所有数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ghibli AI Backend",
    description="AI图片处理服务 - 可扩展的图像处理API，支持用户注册登录",
    version="1.0.0"
)

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request, call_next):
    import time
    start_time = time.time()
    
    # 记录请求详情
    print(f"🔵 [REQUEST] {request.method} {request.url}")
    print(f"🔵 [HEADERS] {dict(request.headers)}")
    
    # 如果是POST请求，尝试记录body（小心处理）
    if request.method == "POST":
        try:
            body = await request.body()
            if len(body) < 1000:  # 只记录小的body
                print(f"🔵 [BODY] {body.decode('utf-8', errors='ignore')}")
        except Exception as e:
            print(f"🔵 [BODY ERROR] {e}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"🟢 [RESPONSE] Status: {response.status_code}, Time: {process_time:.3f}s")
    
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "https://lite-ai-web.vercel.app",
        "https://*.vercel.app",
        "http://22d9ec42059e446fb960e64c3dd6c7c3.ap-singapore.myide.io",
        "http://b924ede87fea4efca710303a2b948404.ap-singapore.myide.io",
        "*"  # 临时允许所有域名用于调试
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_processing.router, prefix="/api", tags=["图片处理"])
app.include_router(auth.router, prefix="/api/auth", tags=["用户认证"])

# 创建上传目录
os.makedirs("./uploads", exist_ok=True)

# 添加静态文件服务，用于直接访问图片
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

