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

