import os
import uuid
import logging
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.config import settings
from app.utils.filename_handler import sanitize_filename, generate_unique_filename, get_safe_url_filename

logger = logging.getLogger(__name__)

def validate_image_file(file: UploadFile) -> bool:
    """
    验证上传的文件是否为有效图像
    
    Args:
        file: 上传的文件对象
        
    Returns:
        bool: 是否为有效图像
    """
    try:
        # 检查文件名是否存在
        if not file.filename:
            logger.warning("上传文件缺少文件名")
            return False
        
        # 清理并验证文件名
        safe_filename = sanitize_filename(file.filename)
        logger.info(f"文件名清理: '{file.filename}' -> '{safe_filename}'")
        
        # 检查文件扩展名
        if '.' in safe_filename:
            file_extension = safe_filename.split(".")[-1].lower()
            if file_extension not in settings.allowed_extensions_list:
                logger.warning(f"不支持的文件扩展名: {file_extension}")
                return False
        else:
            logger.warning("文件缺少扩展名")
            return False
        
        # 检查文件大小
        if hasattr(file, 'size') and file.size:
            if file.size > settings.max_file_size:
                logger.warning(f"文件过大: {file.size} > {settings.max_file_size}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"文件验证异常: {str(e)}")
        return False

def save_uploaded_file(file: UploadFile) -> str:
    """
    保存上传的文件（支持特殊字符文件名）
    
    Args:
        file: 上传的文件对象
        
    Returns:
        str: 保存的文件路径
    """
    try:
        # 确保上传目录存在
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # 处理文件名
        if not file.filename:
            # 如果没有文件名，生成一个默认名称
            original_filename = "uploaded_image.png"
        else:
            original_filename = file.filename
        
        # 生成唯一且安全的文件名
        unique_filename = generate_unique_filename(original_filename, settings.upload_dir)
        file_path = os.path.join(settings.upload_dir, unique_filename)
        
        logger.info(f"保存文件: '{original_filename}' -> '{unique_filename}'")
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            # 重置文件指针
            if hasattr(file.file, 'seek'):
                file.file.seek(0)
            
            content = file.file.read()
            if not content:
                raise ValueError("文件内容为空")
            
            buffer.write(content)
            buffer.flush()
            os.fsync(buffer.fileno())  # 强制写入磁盘
        
        # 验证文件是否成功保存
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise Exception("文件保存失败")
        
        logger.info(f"文件保存成功: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"保存上传文件失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")

def save_processed_image(image_data: bytes, original_filename: str) -> str:
    """
    保存处理后的图像（支持特殊字符文件名）
    
    Args:
        image_data: 图像二进制数据
        original_filename: 原始文件名
        
    Returns:
        str: 保存的文件路径
    """
    try:
        # 确保上传目录存在
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # 验证图像数据
        if not image_data:
            raise ValueError("图像数据为空")
        
        # 处理原始文件名
        if not original_filename:
            original_filename = "processed_image"
        
        # 清理原始文件名并生成处理后的文件名
        safe_base_name = sanitize_filename(original_filename, preserve_extension=False)
        
        # 生成处理后文件的文件名
        unique_id = str(uuid.uuid4())[:8]
        processed_filename = f"{safe_base_name}_processed_{unique_id}.png"
        
        # 确保文件名唯一
        final_filename = generate_unique_filename(processed_filename, settings.upload_dir)
        file_path = os.path.join(settings.upload_dir, final_filename)
        
        logger.info(f"保存处理后图像: '{original_filename}' -> '{final_filename}'")
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            buffer.write(image_data)
            buffer.flush()
            os.fsync(buffer.fileno())  # 强制写入磁盘
        
        # 验证文件是否成功保存
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise Exception("处理后图像保存失败")
        
        logger.info(f"处理后图像保存成功: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"保存处理后图像失败: {str(e)}")
        # 尝试使用备用文件名
        try:
            fallback_filename = f"processed_{uuid.uuid4().hex[:8]}.png"
            fallback_path = os.path.join(settings.upload_dir, fallback_filename)
            
            with open(fallback_path, "wb") as buffer:
                buffer.write(image_data)
            
            logger.info(f"使用备用文件名保存成功: {fallback_path}")
            return fallback_path
            
        except Exception as fallback_error:
            logger.error(f"备用保存方案也失败: {str(fallback_error)}")
            raise HTTPException(status_code=500, detail=f"图像保存失败: {str(e)}")

def get_file_url(file_path: str) -> str:
    """
    获取文件的访问URL（支持特殊字符）
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件访问URL
    """
    try:
        filename = os.path.basename(file_path)
        
        # 获取URL安全的文件名
        safe_url_filename = get_safe_url_filename(filename)
        
        # 构建URL
        file_url = f"/api/files/{safe_url_filename}"
        
        logger.debug(f"生成文件URL: '{filename}' -> '{file_url}'")
        return file_url
        
    except Exception as e:
        logger.error(f"生成文件URL失败: {str(e)}")
        # 返回基本URL作为备用
        filename = os.path.basename(file_path)
        return f"/api/files/{filename}"

def cleanup_file(file_path: str) -> bool:
    """
    清理文件
    
    Args:
        file_path: 要删除的文件路径
        
    Returns:
        bool: 是否成功删除
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"文件清理成功: {file_path}")
            return True
        else:
            logger.info(f"文件不存在，无需清理: {file_path}")
            return True
    except Exception as e:
        logger.error(f"文件清理失败: {file_path}, 错误: {str(e)}")
        return False

def get_file_info(file_path: str) -> dict:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 文件信息
    """
    try:
        if not os.path.exists(file_path):
            return {"exists": False, "error": "文件不存在"}
        
        stat_info = os.stat(file_path)
        filename = os.path.basename(file_path)
        
        return {
            "exists": True,
            "filename": filename,
            "size": stat_info.st_size,
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "is_file": os.path.isfile(file_path),
            "absolute_path": os.path.abspath(file_path)
        }
        
    except Exception as e:
        return {"exists": False, "error": str(e)}
