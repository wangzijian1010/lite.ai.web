from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import json
import io
from PIL import Image
import requests
import time

from app.models.schemas import ImageProcessResponse, ErrorResponse, TextToImageAsyncResponse, ProgressResponse, CreditResponse
from app.models.models import User
from app.database import get_db
from app.routers.auth import get_current_user
from app.utils.credits import check_user_credits, deduct_user_credits
from app.services.image_processing import image_processing_service
from app.utils.file_utils import (
    validate_image_file, 
    save_uploaded_file, 
    save_processed_image, 
    get_file_url,
    cleanup_file
)
from app.config import settings

router = APIRouter()

# 存储任务进度的字典
task_progress = {}

@router.get("/progress/{task_id}")
async def get_task_progress(task_id: str):
    """
    查询任务进度
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务进度信息
    """
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    progress_info = task_progress[task_id]
    
    # 如果任务已完成超过10分钟，清理进度信息
    if progress_info.get('status') == 'completed' and time.time() - progress_info.get('completed_at', 0) > 600:
        del task_progress[task_id]
        raise HTTPException(status_code=404, detail="任务已过期")
    
    return {
        "success": True,
        "task_id": task_id,
        "status": progress_info.get('status', 'unknown'),
        "progress": progress_info.get('progress', 0),
        "message": progress_info.get('message', ''),
        "result_url": progress_info.get('result_url', None),
        "error": progress_info.get('error', None)
    }

@router.get("/processors")
async def get_available_processors():
    """
    获取所有可用的图像处理器
    
    这个端点让前端开发者知道有哪些处理功能可用
    """
    processors = image_processing_service.get_available_processors()
    return {
        "success": True,
        "processors": processors,
        "message": "获取处理器列表成功"
    }

@router.get("/files/{filename}")
async def get_file(filename: str):
    """
    获取处理后的文件（用于图片预览，无需登录）
    
    Args:
        filename: 文件名
        
    Returns:
        FileResponse: 文件响应
    """
    try:
        # URL decode the filename
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename)
        
        # Ensure the file path is safe and within the uploads directory
        file_path = os.path.abspath(os.path.join(settings.upload_dir, decoded_filename))
        uploads_dir = os.path.abspath(settings.upload_dir)
        
        # Security check to prevent directory traversal
        if not file_path.startswith(uploads_dir):
            raise HTTPException(status_code=400, detail="无效的文件路径")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {decoded_filename}")

        # 对于图片预览，直接返回文件
        return FileResponse(
            file_path,
            media_type="image/png"
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文件时出错: {str(e)}")

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    下载处理后的文件（需要登录和积分）
    
    Args:
        filename: 文件名
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        FileResponse: 文件下载响应
    """
    try:
        # URL decode the filename (handle spaces and special characters)
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename)
        
        # Ensure the file path is safe and within the uploads directory
        file_path = os.path.abspath(os.path.join(settings.upload_dir, decoded_filename))
        uploads_dir = os.path.abspath(settings.upload_dir)
        
        # Security check to prevent directory traversal
        if not file_path.startswith(uploads_dir):
            raise HTTPException(status_code=400, detail="无效的文件路径")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"文件不存在: {decoded_filename}")
        
        # 检查积分是否足够
        required_credits = 10
        if not check_user_credits(current_user, required_credits):
            raise HTTPException(
                status_code=400, 
                detail=f"积分不足，当前积分：{current_user.credits}，需要积分：{required_credits}"
            )
        
        # 扣除积分
        success = deduct_user_credits(db, current_user, required_credits)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="积分扣除失败"
            )

        # 返回下载文件
        headers = {"Content-Disposition": f"attachment; filename=\"{decoded_filename}\""}
        
        return FileResponse(
            file_path,
            media_type="image/png",
            headers=headers
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Error in download_file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载文件时出错: {str(e)}")

@router.post("/process", response_model=ImageProcessResponse)
async def process_image(
    file: UploadFile = File(..., description="要处理的图像文件"),
    processing_type: str = Form(..., description="处理类型"),
    parameters: Optional[str] = Form(None, description="处理参数 (JSON格式)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    处理图像的主要端点（需要登录）
    
    Args:
        file: 上传的图像文件
        processing_type: 处理类型 (grayscale, ghibli_style 等)
        parameters: 可选的处理参数，JSON字符串格式
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        ImageProcessResponse: 处理结果
    """
    try:
        # 检查积分是否足够
        required_credits = 10
        if not check_user_credits(current_user, required_credits):
            raise HTTPException(
                status_code=400, 
                detail=f"积分不足，当前积分：{current_user.credits}，需要积分：{required_credits}。请充值后再试。"
            )
            
        # 扣除积分
        success = deduct_user_credits(db, current_user, required_credits)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="积分扣除失败"
            )
        
        # 验证文件
        if not validate_image_file(file):
            raise HTTPException(
                status_code=400, 
                detail="无效的图像文件或文件过大"
            )
        
        # 解析参数
        process_parameters = {}
        if parameters:
            try:
                process_parameters = json.loads(parameters)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="参数格式错误，应为有效的JSON字符串"
                )
        
        # 读取文件内容
        file_content = await file.read()
        
        # 处理图像
        try:
            processed_data, processing_time = image_processing_service.process_image(
                file_content, 
                processing_type, 
                process_parameters
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"图像处理失败: {str(e)}"
            )
        
        # 保存处理后的图像
        processed_file_path = save_processed_image(
            processed_data, 
            file.filename or "image"
        )
        
        # 生成访问URL
        processed_image_url = get_file_url(processed_file_path)
        
        return ImageProcessResponse(
            success=True,
            message="图像处理成功",
            processed_image_url=processed_image_url,
            processing_type=processing_type,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.post("/convert-to-ghibli")
async def convert_to_ghibli_style(
    file: UploadFile = File(..., description="要转换的图像文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    专门的吉卜力风格转换端点（需要登录）
    
    这是为了兼容现有前端代码而创建的便捷端点
    """
    return await process_image(
        file=file, 
        processing_type="ghibli_style", 
        parameters=None,
        current_user=current_user,
        db=db
    )