from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
import json
import io
from PIL import Image

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

@router.post("/text-to-image", response_model=ImageProcessResponse)
async def text_to_image(
    prompt: str = Form(..., description="正向提示词"),
    negative_prompt: str = Form("text, watermark", description="负向提示词"),
    model: Optional[str] = Form(None, description="模型名称"),
    width: int = Form(512, description="图片宽度"),
    height: int = Form(512, description="图片高度"),
    steps: int = Form(20, description="采样步数"),
    cfg: float = Form(8.0, description="CFG值")
):
    """
    ComfyUI 文生图端点
    
    Args:
        prompt: 正向提示词 (必填)
        negative_prompt: 负向提示词 (默认: "text, watermark")
        model: 模型名称 (可选)
        width: 图片宽度 (默认: 512)
        height: 图片高度 (默认: 512)
        steps: 采样步数 (默认: 20)
        cfg: CFG值 (默认: 8.0)
    
    Returns:
        ImageProcessResponse: 生成结果
    
    Example:
        curl -X POST "http://localhost:8000/api/text-to-image" \
             -F "prompt=a beautiful landscape" \
             -F "negative_prompt=blurry, low quality" \
             -F "model=epicphotogasm_ultimateFidelity.safetensors"
    """
    try:
        # 准备参数
        parameters = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg": cfg
        }
        
        if model:
            parameters["model"] = model
        
        # 验证参数
        processor = image_processing_service.processors.get("text_to_image")
        if not processor:
            raise HTTPException(status_code=500, detail="文生图处理器未找到")
        
        if not processor.validate_parameters(parameters):
            raise HTTPException(status_code=400, detail="参数验证失败")
        
        # 处理图像（注意：文生图不需要输入图像）
        try:
            # 创建一个虚拟的图像数据，因为 process_image 期望图像数据
            dummy_image = Image.new('RGB', (1, 1), color=(255, 255, 255))
            dummy_buffer = io.BytesIO()
            dummy_image.save(dummy_buffer, format='PNG')
            dummy_data = dummy_buffer.getvalue()
            
            processed_data, processing_time = image_processing_service.process_image(
                dummy_data, 
                "text_to_image", 
                parameters
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"文生图处理失败: {str(e)}"
            )
        
        # 保存生成的图像
        processed_file_path = save_processed_image(
            processed_data, 
            f"text_to_image_{prompt[:20]}"
        )
        
        # 生成访问URL
        processed_image_url = get_file_url(processed_file_path)
        
        return ImageProcessResponse(
            success=True,
            message="文生图生成成功",
            processed_image_url=processed_image_url,
            processing_type="text_to_image",
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )