from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import image_processing
import os

app = FastAPI(
    title="Ghibli AI Backend",
    description="AI图片处理服务 - 可扩展的图像处理API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_processing.router, prefix="/api", tags=["图片处理"])

os.makedirs("./uploads", exist_ok=True)

@app.get("/")
async def root():
    return {
        "message": "Ghibli AI Backend API", 
        "version": "1.0.0",
        "docs": "/docs"
    }