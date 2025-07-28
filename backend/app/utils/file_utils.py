import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.config import settings

def validate_image_file(file: UploadFile) -> bool:
    """
    验证上传的文件是否为有效图像
    
    Args:
        file: 上传的文件对象
        
    Returns:
        bool: 是否为有效图像
    """
    # 检查文件扩展名
    if file.filename:
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in settings.allowed_extensions_list:
            return False
    
    # 检查文件大小
    if file.size and file.size > settings.max_file_size:
        return False
    
    return True

def save_uploaded_file(file: UploadFile) -> str:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        
    Returns:
        str: 保存的文件路径
    """
    # 生成唯一文件名
    file_extension = file.filename.split(".")[-1].lower() if file.filename else "png"
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.upload_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = file.file.read()
        buffer.write(content)
    
    return file_path

def save_processed_image(image_data: bytes, original_filename: str) -> str:
    """
    保存处理后的图像
    
    Args:
        image_data: 图像二进制数据
        original_filename: 原始文件名
        
    Returns:
        str: 保存的文件路径
    """
    # 生成处理后文件的文件名
    base_name = os.path.splitext(original_filename)[0]
    processed_filename = f"{base_name}_processed_{uuid.uuid4()}.png"
    file_path = os.path.join(settings.upload_dir, processed_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        buffer.write(image_data)
    
    return file_path

def get_file_url(file_path: str) -> str:
    """
    获取文件的访问URL
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件访问URL
    """
    filename = os.path.basename(file_path)
    return f"/api/uploads/{filename}"

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
            return True
    except Exception:
        pass
    return False