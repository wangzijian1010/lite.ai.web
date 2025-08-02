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
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

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
from app.utils.redis_client import task_progress_manager, comfyui_cache_manager

router = APIRouter()

# 任务进度现在使用Redis存储，不再需要内存字典
# task_progress = {}  # 已替换为Redis

@router.get("/progress/{task_id}")
async def get_task_progress(task_id: str):
    """
    查询任务进度
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务进度信息
    """
    # 使用Redis获取任务进度
    progress_info = task_progress_manager.get_progress(task_id)
    
    if not progress_info:
        raise HTTPException(status_code=404, detail="任务不存在或已过期")
    
    # 检查任务是否已完成超过10分钟
    if (progress_info.get('status') == 'completed' and 
        'completed_at' in progress_info and
        time.time() - float(progress_info.get('completed_at', 0)) > 600):
        # 删除过期的任务进度
        task_progress_manager.delete_progress(task_id)
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

@router.get("/comfyui-models")
async def get_comfyui_models():
    """
    获取ComfyUI可用的模型列表（带Redis缓存）
    """
    try:
        # 先尝试从Redis缓存获取
        cached_models = comfyui_cache_manager.get_cached_models()
        if cached_models is not None:
            print(f"🚀 从Redis缓存获取到 {len(cached_models)} 个模型")
            return {
                "success": True,
                "models": cached_models,
                "message": f"获取到 {len(cached_models)} 个可用模型（缓存）",
                "from_cache": True
            }
        
        # 缓存未命中，请求ComfyUI API
        print("📡 缓存未命中，正在请求ComfyUI API...")
        
        # 准备请求头
        headers = {}
        if settings.comfyui_token:
            headers['Authorization'] = f'Bearer {settings.comfyui_token}'
        
        # 请求ComfyUI的模型列表
        response = requests.get(
            f"http://{settings.comfyui_server_address}/object_info", 
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            object_info = response.json()
            
            # 提取CheckpointLoaderSimple的可用模型
            checkpoint_loader = object_info.get("CheckpointLoaderSimple", {})
            input_info = checkpoint_loader.get("input", {})
            ckpt_name_info = input_info.get("ckpt_name", {})
            
            if isinstance(ckpt_name_info, list) and len(ckpt_name_info) > 0:
                models = ckpt_name_info[0] if isinstance(ckpt_name_info[0], list) else []
            else:
                models = []
            
            # 缓存模型列表（1小时过期）
            comfyui_cache_manager.cache_models(models, expire=3600)
            
            print(f"✅ 从ComfyUI获取到 {len(models)} 个模型并已缓存")
            
            return {
                "success": True,
                "models": models,
                "message": f"获取到 {len(models)} 个可用模型",
                "from_cache": False
            }
        else:
            print(f"ComfyUI模型列表请求失败: {response.status_code}")
            return {
                "success": False,
                "models": [],
                "message": f"获取模型列表失败: HTTP {response.status_code}"
            }
            
    except requests.exceptions.ConnectionError:
        print("无法连接到ComfyUI服务器")
        return {
            "success": False,
            "models": [],
            "message": "无法连接到ComfyUI服务器"
        }
    except Exception as e:
        print(f"获取ComfyUI模型列表时出错: {e}")
        return {
            "success": False,
            "models": [],
            "message": f"获取模型列表时出错: {str(e)}"
        }

@router.get("/files/{filename}")
async def get_file(filename: str):
    """
    获取处理后的文件（用于图片预览，无需登录）
    支持包含特殊字符的文件名
    
    Args:
        filename: 文件名（可能包含URL编码）
        
    Returns:
        FileResponse: 文件响应
    """
    try:
        # URL decode the filename to handle special characters
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename, encoding='utf-8')
        
        # Additional decoding for double-encoded filenames
        try:
            decoded_filename = urllib.parse.unquote(decoded_filename, encoding='utf-8')
        except:
            pass  # If second decode fails, use first result
        
        # Log the filename handling for debugging
        print(f"🔍 [FILE ACCESS] Original: '{filename}' -> Decoded: '{decoded_filename}'")
        
        # Ensure the file path is safe and within the uploads directory
        file_path = os.path.abspath(os.path.join(settings.upload_dir, decoded_filename))
        uploads_dir = os.path.abspath(settings.upload_dir)
        
        # Security check to prevent directory traversal
        if not file_path.startswith(uploads_dir):
            print(f"🚨 [SECURITY] Path traversal attempt: {file_path}")
            raise HTTPException(status_code=400, detail="无效的文件路径")
        
        if not os.path.exists(file_path):
            print(f"❌ [FILE NOT FOUND] Path: {file_path}")
            raise HTTPException(status_code=404, detail=f"文件不存在: {decoded_filename}")

        # Determine media type based on file extension
        file_extension = decoded_filename.lower().split('.')[-1] if '.' in decoded_filename else 'png'
        media_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        media_type = media_type_map.get(file_extension, 'image/png')
        
        print(f"✅ [FILE SERVED] Path: {file_path}, Type: {media_type}")
        
        # Return file with appropriate headers for special characters
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename*=UTF-8''{urllib.parse.quote(decoded_filename)}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"🔴 [FILE ERROR] Error in get_file: {str(e)}")
        print(f"🔴 [FILE ERROR] Original filename: '{filename}'")
        raise HTTPException(status_code=500, detail=f"获取文件时出错: {str(e)}")

@router.get("/download/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    下载处理后的文件（需要登录和积分）
    支持包含特殊字符的文件名
    
    Args:
        filename: 文件名（可能包含URL编码）
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        FileResponse: 文件下载响应
    """
    try:
        # URL decode the filename to handle special characters
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename, encoding='utf-8')
        
        # Additional decoding for double-encoded filenames
        try:
            decoded_filename = urllib.parse.unquote(decoded_filename, encoding='utf-8')
        except:
            pass  # If second decode fails, use first result
        
        # Log the download request
        print(f"🔍 [DOWNLOAD] User: {current_user.email}, File: '{decoded_filename}'")
        
        # Ensure the file path is safe and within the uploads directory
        file_path = os.path.abspath(os.path.join(settings.upload_dir, decoded_filename))
        uploads_dir = os.path.abspath(settings.upload_dir)
        
        # Security check to prevent directory traversal
        if not file_path.startswith(uploads_dir):
            print(f"🚨 [SECURITY] Download path traversal attempt: {file_path}")
            raise HTTPException(status_code=400, detail="无效的文件路径")
        
        if not os.path.exists(file_path):
            print(f"❌ [DOWNLOAD] File not found: {file_path}")
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

        # Determine media type based on file extension
        file_extension = decoded_filename.lower().split('.')[-1] if '.' in decoded_filename else 'png'
        media_type_map = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'webp': 'image/webp',
            'gif': 'image/gif'
        }
        media_type = media_type_map.get(file_extension, 'image/png')
        
        # Create proper headers for download with special character support
        safe_filename = urllib.parse.quote(decoded_filename)
        headers = {
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}; filename=\"{decoded_filename.encode('ascii', 'ignore').decode('ascii')}\""
        }
        
        print(f"✅ [DOWNLOAD] File served: {file_path}")
        
        return FileResponse(
            file_path,
            media_type=media_type,
            headers=headers
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"🔴 [DOWNLOAD ERROR] Error in download_file: {str(e)}")
        print(f"🔴 [DOWNLOAD ERROR] Original filename: '{filename}'")
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

@router.post("/ghibli-style-async")
async def ghibli_style_async(
    file: UploadFile = File(..., description="要转换的图像文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    异步吉卜力风格转换端点（支持进度跟踪）
    
    Args:
        file: 上传的图像文件
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        AsyncTaskResponse: 任务ID和状态
    """
    import uuid
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
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
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务进度（使用Redis）
        task_progress_manager.set_progress(task_id, {
            'status': 'pending',
            'progress': 0,
            'message': '任务已创建，准备转换为吉卜力风格...',
            'result_url': None,
            'error': None,
            'created_at': time.time()
        })
        
        # 读取文件内容
        file_content = await file.read()
        
        # 启动后台任务
        asyncio.create_task(ghibli_style_background(
            task_id, file_content, file.filename or "image"
        ))
        
        return {
            "success": True,
            "message": "吉卜力风格转换任务已创建",
            "task_id": task_id,
            "estimated_time": 90  # 预估1.5分钟
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建吉卜力风格转换任务失败: {str(e)}"
        )

async def ghibli_style_background(task_id: str, file_content: bytes, filename: str):
    """
    后台吉卜力风格转换任务
    """
    try:
        # 更新任务状态（使用Redis）
        task_progress_manager.update_progress(task_id, {
            'status': 'running',
            'progress': 10,
            'message': '开始转换为吉卜力风格...'
        })
        
        # 在线程池中执行图像处理（因为图像处理是CPU密集型任务）
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            processed_data, processing_time = await loop.run_in_executor(
                executor,
                image_processing_service.process_image,
                file_content,
                'ghibli_style',
                {},
                task_id  # 传递task_id用于进度更新
            )
        
        # 保存处理后的图像
        processed_file_path = save_processed_image(processed_data, filename)
        
        # 生成访问URL
        processed_image_url = get_file_url(processed_file_path)
        
        # 更新任务完成状态
        task_progress_manager.update_progress(task_id, {
            'status': 'completed',
            'progress': 100,
            'message': '吉卜力风格转换完成',
            'result_url': processed_image_url,
            'completed_at': time.time()
        })
        
    except Exception as e:
        # 更新任务失败状态
        task_progress_manager.update_progress(task_id, {
            'status': 'failed',
            'progress': 0,
            'message': '吉卜力风格转换失败',
            'error': str(e)
        })
        print(f"❌ [GHIBLI ASYNC TASK] Task {task_id} failed: {str(e)}")



@router.post("/process-async")
async def process_image_async(
    file: UploadFile = File(..., description="要处理的图像文件"),
    processing_type: str = Form(..., description="处理类型"),
    parameters: Optional[str] = Form(None, description="处理参数 (JSON格式)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    异步处理图像的端点（支持进度跟踪）
    
    Args:
        file: 上传的图像文件
        processing_type: 处理类型 (creative_upscale, ghibli_style 等)
        parameters: 可选的处理参数，JSON字符串格式
        current_user: 当前登录用户
        db: 数据库会话
    
    Returns:
        AsyncTaskResponse: 任务ID和状态
    """
    import uuid
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
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
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务进度
        task_progress_manager.set_progress(task_id, {
            'status': 'pending',
            'progress': 0,
            'message': '任务已创建，准备处理...',
            'result_url': None,
            'error': None,
            'created_at': time.time()
        })
        
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
        
        # 启动后台任务
        asyncio.create_task(process_image_background(
            task_id, file_content, processing_type, process_parameters, file.filename or "image"
        ))
        
        return {
            "success": True,
            "message": "任务已创建",
            "task_id": task_id,
            "estimated_time": 120  # 预估2分钟
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建任务失败: {str(e)}"
        )

async def process_image_background(task_id: str, file_content: bytes, processing_type: str, parameters: dict, filename: str):
    """
    后台处理图像任务
    """
    try:
        # 更新任务状态
        task_progress_manager.update_progress(task_id, {
            'status': 'running',
            'progress': 10,
            'message': '开始处理图像...'
        })
        
        # 在线程池中执行图像处理（因为图像处理是CPU密集型任务）
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            processed_data, processing_time = await loop.run_in_executor(
                executor,
                image_processing_service.process_image,
                file_content,
                processing_type,
                parameters,
                task_id  # 传递task_id用于进度更新
            )
        
        # 保存处理后的图像
        processed_file_path = save_processed_image(processed_data, filename)
        
        # 生成访问URL
        processed_image_url = get_file_url(processed_file_path)
        
        # 更新任务完成状态
        task_progress_manager.update_progress(task_id, {
            'status': 'completed',
            'progress': 100,
            'message': '处理完成',
            'result_url': processed_image_url,
            'completed_at': time.time()
        })
        
    except Exception as e:
        # 更新任务失败状态
        task_progress_manager.update_progress(task_id, {
            'status': 'failed',
            'progress': 0,
            'message': '处理失败',
            'error': str(e)
        })
        print(f"❌ [ASYNC TASK] Task {task_id} failed: {str(e)}")

@router.post("/text-to-image-async")
async def text_to_image_async(
    prompt: str = Form(..., description="正向提示词"),
    negative_prompt: Optional[str] = Form(None, description="负向提示词"),
    model: Optional[str] = Form(None, description="模型名称"),
    width: Optional[int] = Form(512, description="图像宽度"),
    height: Optional[int] = Form(512, description="图像高度"),
    steps: Optional[int] = Form(20, description="采样步数"),
    cfg: Optional[float] = Form(8.0, description="CFG值"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    异步文生图端点（支持进度跟踪）
    """
    import uuid
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
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
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务进度
        task_progress_manager.set_progress(task_id, {
            'status': 'pending',
            'progress': 0,
            'message': '任务已创建，准备生成图像...',
            'result_url': None,
            'error': None,
            'created_at': time.time()
        })
        
        # 准备文生图参数
        text_to_image_params = {
            'prompt': prompt,
            'negative_prompt': negative_prompt or 'text, watermark, blurry, low quality',
            'model': model,
            'width': width,
            'height': height,
            'steps': steps,
            'cfg': cfg
        }
        
        # 启动后台任务
        asyncio.create_task(text_to_image_background(task_id, text_to_image_params))
        
        return {
            "success": True,
            "message": "文生图任务已创建",
            "task_id": task_id,
            "estimated_time": 180  # 预估3分钟
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建文生图任务失败: {str(e)}"
        )

async def text_to_image_background(task_id: str, parameters: dict):
    """
    后台文生图任务
    """
    try:
        # 更新任务状态
        task_progress_manager.update_progress(task_id, {
            'status': 'running',
            'progress': 10,
            'message': '开始生成图像...'
        })
        
        # 在线程池中执行文生图处理
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            processed_data, processing_time = await loop.run_in_executor(
                executor,
                image_processing_service.process_image,
                b'',  # 文生图不需要输入图像
                'text_to_image',
                parameters,
                task_id  # 传递task_id用于进度更新
            )
        
        # 保存生成的图像
        processed_file_path = save_processed_image(processed_data, "generated_image")
        
        # 生成访问URL
        processed_image_url = get_file_url(processed_file_path)
        
        # 更新任务完成状态
        task_progress_manager.update_progress(task_id, {
            'status': 'completed',
            'progress': 100,
            'message': '图像生成完成',
            'result_url': processed_image_url,
            'completed_at': time.time()
        })
        
    except Exception as e:
        # 更新任务失败状态
        task_progress_manager.update_progress(task_id, {
            'status': 'failed',
            'progress': 0,
            'message': '生成失败',
            'error': str(e)
        })
        print(f"❌ [TEXT-TO-IMAGE TASK] Task {task_id} failed: {str(e)}")

@router.post("/upscale")
async def upscale_image(
    file: UploadFile = File(..., description="要放大的图像文件"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    专门的图像高清放大端点（需要登录）
    """
    return await process_image(
        file=file, 
        processing_type="creative_upscale", 
        parameters=None,
        current_user=current_user,
        db=db
    )
