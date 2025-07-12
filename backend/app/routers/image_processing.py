from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
from typing import Optional
import os
import json
import io
from PIL import Image
import requests
import time

from app.models.schemas import ImageProcessResponse, ErrorResponse, TextToImageAsyncResponse, ProgressResponse
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

@router.get("/comfyui-progress/{prompt_id}")
async def get_comfyui_progress(prompt_id: str):
    """
    查询ComfyUI任务进度
    
    Args:
        prompt_id: ComfyUI的prompt_id
        
    Returns:
        ComfyUI任务进度信息
    """
    try:
        server_address = settings.comfyui_server_address
        
        # 查询队列状态
        queue_response = requests.get(f"http://{server_address}/queue", timeout=5)
        queue_data = queue_response.json()
        
        # 查询历史状态
        history_response = requests.get(f"http://{server_address}/history/{prompt_id}", timeout=5)
        history_data = history_response.json()
        
        # 如果在历史中找到，说明已完成
        if prompt_id in history_data:
            return {
                "success": True,
                "status": "completed",
                "progress": 100,
                "message": "任务已完成"
            }
        
        # 检查是否在队列中
        running_queue = queue_data.get('queue_running', [])
        pending_queue = queue_data.get('queue_pending', [])
        
        # 检查正在执行的任务
        for item in running_queue:
            if len(item) >= 2 and item[1] == prompt_id:
                return {
                    "success": True,
                    "status": "running",
                    "progress": 50,  # 假设运行中为50%
                    "message": "正在生成图像..."
                }
        
        # 检查等待队列
        for i, item in enumerate(pending_queue):
            if len(item) >= 2 and item[1] == prompt_id:
                total_pending = len(pending_queue)
                position = i + 1
                return {
                    "success": True,
                    "status": "pending",
                    "progress": 0,
                    "message": f"排队中... ({position}/{total_pending})"
                }
        
        # 如果都没找到，可能任务失败或不存在
        return {
            "success": False,
            "status": "not_found",
            "progress": 0,
            "message": "任务未找到"
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "progress": 0,
            "message": f"查询进度失败: {str(e)}"
        }

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

@router.get("/comfyui-models")
async def get_comfyui_models():
    """
    获取ComfyUI可用的模型列表
    
    Returns:
        可用模型列表
    """
    try:
        server_address = settings.comfyui_server_address
        
        # 查询ComfyUI的模型列表
        response = requests.get(f"http://{server_address}/object_info", timeout=10)
        
        if response.status_code == 200:
            object_info = response.json()
            
            # 提取checkpoint模型
            checkpoint_models = []
            if "CheckpointLoaderSimple" in object_info:
                checkpoint_info = object_info["CheckpointLoaderSimple"]
                if "input" in checkpoint_info and "required" in checkpoint_info["input"]:
                    ckpt_name_info = checkpoint_info["input"]["required"].get("ckpt_name")
                    if ckpt_name_info and isinstance(ckpt_name_info, list) and len(ckpt_name_info) > 0:
                        checkpoint_models = ckpt_name_info[0] if isinstance(ckpt_name_info[0], list) else []
            
            return {
                "success": True,
                "models": checkpoint_models,
                "message": f"找到 {len(checkpoint_models)} 个可用模型"
            }
        else:
            return {
                "success": False,
                "models": [],
                "message": f"无法连接到ComfyUI服务器: HTTP {response.status_code}"
            }
            
    except requests.exceptions.ConnectTimeoutError:
        return {
            "success": False,
            "models": [],
            "message": "连接ComfyUI服务器超时"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "models": [],
            "message": "无法连接到ComfyUI服务器"
        }
    except Exception as e:
        return {
            "success": False,
            "models": [],
            "message": f"获取模型列表失败: {str(e)}"
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

@router.post("/text-to-image-async", response_model=TextToImageAsyncResponse)
async def text_to_image_async(
    prompt: str = Form(..., description="正向提示词"),
    negative_prompt: str = Form("text, watermark", description="负向提示词"),
    model: Optional[str] = Form(None, description="模型名称"),
    width: int = Form(512, description="图片宽度"),
    height: int = Form(512, description="图片高度"),
    steps: int = Form(20, description="采样步数"),
    cfg: float = Form(8.0, description="CFG值")
):
    """
    ComfyUI 异步文生图端点
    返回任务ID，可通过进度查询接口获取实时进度
    """
    import uuid
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        task_progress[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "任务已创建，准备开始生成...",
            "started_at": time.time()
        }
        
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
        
        # 异步启动处理任务
        asyncio.create_task(process_text_to_image_async(task_id, parameters))
        
        return TextToImageAsyncResponse(
            success=True,
            message="任务已创建，正在处理中",
            task_id=task_id,
            estimated_time=60  # 估计60秒完成
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建任务失败: {str(e)}"
        )

async def process_text_to_image_async(task_id: str, parameters: dict):
    """异步处理文生图任务"""
    try:
        # 更新状态为开始处理
        task_progress[task_id].update({
            "status": "running",
            "progress": 10,
            "message": "正在准备生成参数..."
        })
        
        # 创建虚拟图像数据
        dummy_image = Image.new('RGB', (1, 1), color=(255, 255, 255))
        dummy_buffer = io.BytesIO()
        dummy_image.save(dummy_buffer, format='PNG')
        dummy_data = dummy_buffer.getvalue()
        
        # 更新进度
        task_progress[task_id].update({
            "progress": 20,
            "message": "正在连接ComfyUI服务器..."
        })
        
        # 调用处理服务
        def run_processing():
            return image_processing_service.process_image(
                dummy_data, 
                "text_to_image", 
                parameters,
                task_id=task_id  # 传递task_id用于进度更新
            )
        
        # 在线程池中运行同步处理函数
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            processed_data, processing_time = await loop.run_in_executor(
                executor, run_processing
            )
        
        # 保存生成的图像
        task_progress[task_id].update({
            "progress": 90,
            "message": "正在保存图像..."
        })
        
        processed_file_path = save_processed_image(
            processed_data, 
            f"text_to_image_{parameters['prompt'][:20]}"
        )
        
        # 生成访问URL
        processed_image_url = get_file_url(processed_file_path)
        
        # 任务完成
        task_progress[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "图像生成完成",
            "result_url": processed_image_url,
            "completed_at": time.time(),
            "processing_time": processing_time
        })
        
    except Exception as e:
        # 任务失败
        task_progress[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "图像生成失败",
            "error": str(e),
            "completed_at": time.time()
        })

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