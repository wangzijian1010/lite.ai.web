from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
import json

from app.models.schemas import ImageProcessResponse, ErrorResponse
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

@router.post("/process", response_model=ImageProcessResponse)
async def process_image(
    file: UploadFile = File(..., description="要处理的图像文件"),
    processing_type: str = Form(..., description="处理类型"),
    parameters: Optional[str] = Form(None, description="处理参数 (JSON格式)")
):
    """
    处理图像的主要端点
    
    Args:
        file: 上传的图像文件
        processing_type: 处理类型 (grayscale, ghibli_style 等)
        parameters: 可选的处理参数，JSON字符串格式
    
    Returns:
        ImageProcessResponse: 处理结果
    
    Example:
        curl -X POST "http://localhost:8000/api/process" \
             -F "file=@image.jpg" \
             -F "processing_type=grayscale"
    """
    try:
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

@router.get("/files/{filename}")
async def get_file(filename: str):
    """
    获取处理后的文件
    
    Args:
        filename: 文件名
        
    Returns:
        FileResponse: 文件响应
    """
    file_path = os.path.join(settings.upload_dir, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )

@router.post("/convert-to-ghibli")
async def convert_to_ghibli_style(
    file: UploadFile = File(..., description="要转换的图像文件")
):
    """
    专门的吉卜力风格转换端点
    
    这是为了兼容现有前端代码而创建的便捷端点
    """
    return await process_image(
        file=file, 
        processing_type="ghibli_style", 
        parameters=None
    )