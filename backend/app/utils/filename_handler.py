"""
文件名处理工具模块 - 处理包含空格和特殊字符的文件名
"""
import re
import unicodedata
import uuid
from typing import Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FilenameHandler:
    """文件名处理器类"""
    
    # 危险字符列表
    DANGEROUS_CHARS = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    
    # 保留的系统文件名（Windows）
    RESERVED_NAMES = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    def __init__(self):
        self.max_filename_length = 200  # 最大文件名长度
        self.max_extension_length = 10   # 最大扩展名长度
    
    def sanitize_filename(self, filename: str, preserve_extension: bool = True) -> str:
        """
        清理文件名，移除或替换危险字符
        
        Args:
            filename: 原始文件名
            preserve_extension: 是否保留原始扩展名
            
        Returns:
            str: 清理后的安全文件名
        """
        if not filename:
            return f"unnamed_{uuid.uuid4().hex[:8]}"
        
        try:
            # 分离文件名和扩展名
            if preserve_extension and '.' in filename:
                name_part, extension = filename.rsplit('.', 1)
                extension = f".{extension.lower()}"
            else:
                name_part = filename
                extension = ""
            
            # 规范化Unicode字符
            name_part = unicodedata.normalize('NFKD', name_part)
            
            # 移除或替换危险字符
            safe_name = self._remove_dangerous_chars(name_part)
            
            # 处理空格和连续特殊字符
            safe_name = self._normalize_spaces_and_chars(safe_name)
            
            # 检查保留名称
            safe_name = self._handle_reserved_names(safe_name)
            
            # 限制长度
            safe_name = self._limit_length(safe_name, extension)
            
            # 确保文件名不为空
            if not safe_name:
                safe_name = f"file_{uuid.uuid4().hex[:8]}"
            
            # 组合最终文件名
            final_filename = safe_name + extension
            
            logger.info(f"文件名清理: '{filename}' -> '{final_filename}'")
            return final_filename
            
        except Exception as e:
            logger.error(f"文件名清理失败: {str(e)}")
            # 返回安全的备用文件名
            ext = Path(filename).suffix if filename else ""
            return f"safe_file_{uuid.uuid4().hex[:8]}{ext}"
    
    def _remove_dangerous_chars(self, name: str) -> str:
        """移除危险字符"""
        # 移除控制字符和危险字符
        safe_name = name
        for char in self.DANGEROUS_CHARS:
            safe_name = safe_name.replace(char, '_')
        
        # 移除控制字符（ASCII 0-31）
        safe_name = ''.join(char if ord(char) >= 32 else '_' for char in safe_name)
        
        return safe_name
    
    def _normalize_spaces_and_chars(self, name: str) -> str:
        """规范化空格和特殊字符"""
        # 将多个空格替换为单个下划线
        name = re.sub(r'\s+', '_', name)
        
        # 将多个连续的下划线、连字符替换为单个
        name = re.sub(r'[_-]+', '_', name)
        
        # 移除开头和结尾的特殊字符
        name = name.strip('_-. ')
        
        # 只保留字母、数字、下划线、连字符和点
        name = re.sub(r'[^\w\-.]', '_', name)
        
        return name
    
    def _handle_reserved_names(self, name: str) -> str:
        """处理系统保留名称"""
        if name.upper() in self.RESERVED_NAMES:
            return f"{name}_file"
        return name
    
    def _limit_length(self, name: str, extension: str) -> str:
        """限制文件名长度"""
        max_name_length = self.max_filename_length - len(extension)
        
        if len(name) > max_name_length:
            # 保留前面部分和后面部分，中间用hash连接
            if max_name_length > 20:
                front_part = name[:max_name_length//2 - 5]
                back_part = name[-(max_name_length//2 - 5):]
                hash_part = uuid.uuid4().hex[:8]
                name = f"{front_part}_{hash_part}_{back_part}"
            else:
                name = name[:max_name_length]
        
        return name
    
    def generate_unique_filename(self, original_filename: str, directory: str = None) -> str:
        """
        生成唯一的文件名
        
        Args:
            original_filename: 原始文件名
            directory: 目标目录（用于检查重复）
            
        Returns:
            str: 唯一的文件名
        """
        # 首先清理文件名
        clean_filename = self.sanitize_filename(original_filename)
        
        # 如果没有指定目录，直接返回带UUID的文件名
        if not directory:
            name_part, ext = self._split_filename(clean_filename)
            return f"{name_part}_{uuid.uuid4().hex[:8]}{ext}"
        
        # 检查文件是否已存在
        target_path = Path(directory) / clean_filename
        if not target_path.exists():
            return clean_filename
        
        # 如果存在，生成唯一版本
        name_part, ext = self._split_filename(clean_filename)
        counter = 1
        
        while True:
            new_filename = f"{name_part}_{counter}{ext}"
            new_path = Path(directory) / new_filename
            
            if not new_path.exists():
                return new_filename
            
            counter += 1
            
            # 防止无限循环
            if counter > 1000:
                return f"{name_part}_{uuid.uuid4().hex[:8]}{ext}"
    
    def _split_filename(self, filename: str) -> Tuple[str, str]:
        """分离文件名和扩展名"""
        if '.' in filename:
            name_part, ext = filename.rsplit('.', 1)
            return name_part, f".{ext}"
        return filename, ""
    
    def validate_filename(self, filename: str) -> Tuple[bool, str]:
        """
        验证文件名是否安全
        
        Args:
            filename: 要验证的文件名
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        if not filename:
            return False, "文件名不能为空"
        
        if len(filename) > self.max_filename_length:
            return False, f"文件名过长，最大长度: {self.max_filename_length}"
        
        # 检查危险字符
        for char in self.DANGEROUS_CHARS:
            if char in filename:
                return False, f"文件名包含危险字符: {char}"
        
        # 检查保留名称
        name_part = filename.split('.')[0].upper()
        if name_part in self.RESERVED_NAMES:
            return False, f"文件名是系统保留名称: {name_part}"
        
        return True, "文件名验证通过"
    
    def get_safe_url_filename(self, filename: str) -> str:
        """
        获取URL安全的文件名
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: URL安全的文件名
        """
        import urllib.parse
        
        # 首先清理文件名
        safe_filename = self.sanitize_filename(filename)
        
        # URL编码以处理剩余的特殊字符
        url_safe_filename = urllib.parse.quote(safe_filename, safe='.-_')
        
        return url_safe_filename
    
    def extract_file_info(self, filename: str) -> dict:
        """
        提取文件信息
        
        Args:
            filename: 文件名
            
        Returns:
            dict: 文件信息
        """
        info = {
            "original_filename": filename,
            "safe_filename": self.sanitize_filename(filename),
            "name_part": "",
            "extension": "",
            "is_safe": False,
            "issues": []
        }
        
        try:
            # 分离名称和扩展名
            if '.' in filename:
                info["name_part"], ext = filename.rsplit('.', 1)
                info["extension"] = f".{ext.lower()}"
            else:
                info["name_part"] = filename
                info["extension"] = ""
            
            # 验证安全性
            is_safe, message = self.validate_filename(filename)
            info["is_safe"] = is_safe
            
            if not is_safe:
                info["issues"].append(message)
            
            # 检查其他潜在问题
            if len(filename) > 100:
                info["issues"].append("文件名较长，建议缩短")
            
            if any(ord(char) > 127 for char in filename):
                info["issues"].append("包含非ASCII字符，可能在某些系统上出现问题")
            
            if filename.startswith('.'):
                info["issues"].append("隐藏文件，可能不会显示在某些系统中")
            
        except Exception as e:
            info["issues"].append(f"文件信息提取失败: {str(e)}")
        
        return info

# 创建全局实例
filename_handler = FilenameHandler()

# 便捷函数
def sanitize_filename(filename: str, preserve_extension: bool = True) -> str:
    """清理文件名的便捷函数"""
    return filename_handler.sanitize_filename(filename, preserve_extension)

def generate_unique_filename(original_filename: str, directory: str = None) -> str:
    """生成唯一文件名的便捷函数"""
    return filename_handler.generate_unique_filename(original_filename, directory)

def validate_filename(filename: str) -> Tuple[bool, str]:
    """验证文件名的便捷函数"""
    return filename_handler.validate_filename(filename)

def get_safe_url_filename(filename: str) -> str:
    """获取URL安全文件名的便捷函数"""
    return filename_handler.get_safe_url_filename(filename)