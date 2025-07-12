from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import numpy as np
from PIL import Image
import cv2
import io
import base64
import time
import requests
import aiohttp
import asyncio
from app.config import settings

class ImageProcessor(ABC):
    """
    图像处理器基类
    
    所有图像处理功能都应该继承这个类
    这样可以确保一致的接口和易于扩展
    """
    
    @abstractmethod
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        """
        处理图像的抽象方法
        
        Args:
            image: PIL图像对象
            parameters: 处理参数字典
            
        Returns:
            处理后的PIL图像对象
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """返回处理器名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """返回处理器描述"""
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        验证参数有效性
        子类可以重写此方法来添加特定验证
        """
        return True

class GrayscaleProcessor(ImageProcessor):
    """灰度转换处理器"""
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        """将图像转换为灰度"""
        # 转换为OpenCV格式
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 转换为灰度
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # 转换回PIL格式
        return Image.fromarray(gray_image)
    
    def get_name(self) -> str:
        return "grayscale"
    
    def get_description(self) -> str:
        return "将彩色图像转换为灰度图像"

class GhibliStyleProcessor(ImageProcessor):
    """吉卜力风格处理器 (模拟实现)"""
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        """
        模拟吉卜力风格转换
        实际项目中这里会调用真实的AI API
        """
        # 这里只是简单返回原图作为演示
        # 在实际项目中，这里会调用外部AI服务
        
        # 添加一些简单的滤镜效果来模拟处理
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 应用一些基本的图像处理来模拟艺术效果
        # 增强对比度
        alpha = 1.2  # 对比度
        beta = 10    # 亮度
        enhanced = cv2.convertScaleAbs(cv_image, alpha=alpha, beta=beta)
        
        # 应用双边滤波来平滑图像
        smooth = cv2.bilateralFilter(enhanced, 15, 80, 80)
        
        # 转换回PIL格式
        return Image.fromarray(cv2.cvtColor(smooth, cv2.COLOR_BGR2RGB))
    
    def get_name(self) -> str:
        return "ghibli_style"
    
    def get_description(self) -> str:
        return "将图像转换为吉卜力工作室风格（模拟实现）"

class UpscaleProcessor(ImageProcessor):
    """
    图片超分放大处理器
    
    这是一个外部API调用的示例，展示如何集成第三方AI服务
    """
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        """
        使用外部API进行图片超分放大
        
        Args:
            image: 输入图像
            parameters: 处理参数，可包含：
                - scale_factor: 放大倍数 (2, 4, 8)
                - model: 使用的模型 (real-esrgan, esrgan, etc.)
        
        Returns:
            放大后的图像
        """
        # 默认参数
        scale_factor = parameters.get('scale_factor', 2) if parameters else 2
        model = parameters.get('model', 'real-esrgan') if parameters else 'real-esrgan'
        
        try:
            # 方法1: 使用 requests (同步调用)
            result_image = self._call_upscale_api_sync(image, scale_factor, model)
            return result_image
            
        except Exception as e:
            print(f"外部API调用失败: {e}")
            # 如果外部API失败，使用简单的插值放大作为降级方案
            return self._fallback_upscale(image, scale_factor)
    
    def _call_upscale_api_sync(self, image: Image.Image, scale_factor: int, model: str) -> Image.Image:
        """
        同步调用外部超分API
        
        这是一个示例实现，展示如何调用外部AI服务
        """
        # 将图像转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 准备API请求数据
        api_data = {
            "image": image_base64,
            "scale_factor": scale_factor,
            "model": model,
            "format": "png"
        }
        
        headers = {
            "Authorization": f"Bearer {settings.upscale_api_key}",
            "Content-Type": "application/json"
        }
        
        # 发送请求到外部API
        response = requests.post(
            settings.upscale_api_url,
            json=api_data,
            headers=headers,
            timeout=settings.upscale_api_timeout
        )
        
        if response.status_code == 200:
            result_data = response.json()
            
            # 假设API返回格式为 {"success": true, "result_image": "base64_string"}
            if result_data.get("success"):
                result_image_base64 = result_data.get("result_image")
                result_image_data = base64.b64decode(result_image_base64)
                return Image.open(io.BytesIO(result_image_data))
            else:
                raise Exception(f"API返回错误: {result_data.get('message', '未知错误')}")
        else:
            raise Exception(f"API请求失败: HTTP {response.status_code}")
    
    async def _call_upscale_api_async(self, image: Image.Image, scale_factor: int, model: str) -> Image.Image:
        """
        异步调用外部超分API (可选实现)
        
        对于耗时较长的AI处理，建议使用异步调用
        """
        # 将图像转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 准备API请求数据
        api_data = {
            "image": image_base64,
            "scale_factor": scale_factor,
            "model": model,
            "format": "png"
        }
        
        headers = {
            "Authorization": f"Bearer {settings.upscale_api_key}",
            "Content-Type": "application/json"
        }
        
        # 使用aiohttp发送异步请求
        async with aiohttp.ClientSession() as session:
            async with session.post(
                settings.upscale_api_url,
                json=api_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=settings.upscale_api_timeout)
            ) as response:
                if response.status == 200:
                    result_data = await response.json()
                    
                    if result_data.get("success"):
                        result_image_base64 = result_data.get("result_image")
                        result_image_data = base64.b64decode(result_image_base64)
                        return Image.open(io.BytesIO(result_image_data))
                    else:
                        raise Exception(f"API返回错误: {result_data.get('message', '未知错误')}")
                else:
                    raise Exception(f"API请求失败: HTTP {response.status}")
    
    def _fallback_upscale(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """
        降级方案：简单的插值放大
        
        当外部API不可用时使用
        """
        width, height = image.size
        new_size = (width * scale_factor, height * scale_factor)
        
        # 使用双三次插值进行放大
        upscaled = image.resize(new_size, Image.LANCZOS)
        return upscaled
    
    def get_name(self) -> str:
        return "upscale"
    
    def get_description(self) -> str:
        return "使用AI超分技术放大图片，提升分辨率和清晰度"
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证超分参数"""
        if not parameters:
            return True
            
        scale_factor = parameters.get('scale_factor')
        if scale_factor and scale_factor not in [2, 4, 8]:
            return False
            
        return True

class ImageProcessingService:
    """
    图像处理服务管理器
    
    这个类管理所有的图像处理器，提供统一的接口
    添加新功能只需要创建新的处理器并注册即可
    """
    
    def __init__(self):
        self.processors: Dict[str, ImageProcessor] = {}
        self._register_default_processors()
    
    def _register_default_processors(self):
        """注册默认的处理器"""
        self.register_processor(GrayscaleProcessor())
        self.register_processor(GhibliStyleProcessor())
        self.register_processor(UpscaleProcessor())
    
    def register_processor(self, processor: ImageProcessor):
        """
        注册新的图像处理器
        
        Args:
            processor: 图像处理器实例
        """
        self.processors[processor.get_name()] = processor
    
    def get_available_processors(self) -> Dict[str, str]:
        """获取所有可用的处理器"""
        return {
            name: processor.get_description() 
            for name, processor in self.processors.items()
        }
    
    def process_image(
        self, 
        image_data: bytes, 
        processing_type: str, 
        parameters: Dict[str, Any] = None
    ) -> Tuple[bytes, float]:
        """
        处理图像
        
        Args:
            image_data: 图像二进制数据
            processing_type: 处理类型
            parameters: 处理参数
            
        Returns:
            (处理后的图像数据, 处理时间)
        """
        start_time = time.time()
        
        if processing_type not in self.processors:
            raise ValueError(f"不支持的处理类型: {processing_type}")
        
        processor = self.processors[processing_type]
        
        # 验证参数
        if parameters and not processor.validate_parameters(parameters):
            raise ValueError("无效的处理参数")
        
        # 加载图像
        image = Image.open(io.BytesIO(image_data))
        
        # 确保图像是RGB模式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 处理图像
        processed_image = processor.process(image, parameters or {})
        
        # 保存处理后的图像
        output_buffer = io.BytesIO()
        processed_image.save(output_buffer, format='PNG')
        output_data = output_buffer.getvalue()
        
        processing_time = time.time() - start_time
        
        return output_data, processing_time

# 全局服务实例
image_processing_service = ImageProcessingService()