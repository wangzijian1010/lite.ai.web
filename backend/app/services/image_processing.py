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
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None, task_id: str = None) -> Image.Image:
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
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None, task_id: str = None) -> Image.Image:
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
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None, task_id: str = None) -> Image.Image:
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
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None, task_id: str = None) -> Image.Image:
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

class TextToImageProcessor(ImageProcessor):
    """
    ComfyUI 文生图处理器
    
    这个处理器不需要输入图像，而是基于文字描述生成图像
    """
    
    def process(self, image: Image.Image = None, parameters: Dict[str, Any] = None, task_id: str = None) -> Image.Image:
        """
        使用 ComfyUI 进行文生图
        
        Args:
            image: 对于文生图功能，这个参数被忽略
            parameters: 包含文生图参数：
                - prompt: 正向提示词 (必需)
                - negative_prompt: 负向提示词 (可选)
                - model: 模型名称 (可选)
                - width: 图片宽度 (可选, 默认512)
                - height: 图片高度 (可选, 默认512)
                - steps: 采样步数 (可选, 默认20)
                - cfg: CFG值 (可选, 默认8)
        
        Returns:
            生成的图像
        """
        if not parameters or 'prompt' not in parameters:
            raise ValueError("文生图需要提供 prompt 参数")
        
        # 提取参数
        prompt = parameters['prompt']
        negative_prompt = parameters.get('negative_prompt', 'text, watermark')
        model = parameters.get('model', None)
        width = parameters.get('width', 512)
        height = parameters.get('height', 512)
        steps = parameters.get('steps', 20)
        cfg = parameters.get('cfg', 8)
        
        try:
            # 调用 ComfyUI API
            image_data = self._call_comfyui_api(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model=model,
                width=width,
                height=height,
                steps=steps,
                cfg=cfg,
                task_id=task_id
            )
            
            # 将图像数据转换为 PIL Image
            return Image.open(io.BytesIO(image_data))
            
        except Exception as e:
            print(f"ComfyUI API调用失败: {e}")
            # 降级方案：生成一个简单的纯色图像作为占位符
            return self._fallback_generate_placeholder(prompt, width, height)
    
    def _call_comfyui_api(self, prompt: str, negative_prompt: str, model: str = None, 
                         width: int = 512, height: int = 512, steps: int = 20, cfg: int = 8, 
                         task_id: str = None) -> bytes:
        """
        调用 ComfyUI API 生成图像
        
        基于提供的 ComfyUI 客户端代码实现
        """
        import json
        import uuid
        from urllib.parse import urlencode
        
        server_address = settings.comfyui_server_address
        client_id = str(uuid.uuid4())
        
        # 1. 加载工作流模板
        workflow = self._load_workflow_template()
        if not workflow:
            raise Exception("无法加载 ComfyUI 工作流模板")
        
        # 2. 更新工作流参数
        workflow = self._update_workflow_prompts(
            workflow, prompt, negative_prompt, model, width, height, steps, cfg
        )
        
        # 3. 提交到队列
        prompt_data = {"prompt": workflow, "client_id": client_id}
        data = json.dumps(prompt_data).encode('utf-8')
        
        response = requests.post(
            f"http://{server_address}/prompt", 
            data=data,
            timeout=settings.comfyui_timeout
        )
        result = response.json()
        prompt_id = result['prompt_id']
        
        print(f"ComfyUI 任务ID: {prompt_id}")
        
        # 4. 等待完成
        history = self._wait_for_completion(server_address, prompt_id, task_id)
        
        # 5. 获取生成的图像
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                for image_info in node_output['images']:
                    image_data = self._get_image(
                        server_address, image_info['filename'], 
                        image_info['subfolder'], image_info['type']
                    )
                    return image_data
        
        raise Exception("未能从 ComfyUI 获取生成的图像")
    
    def _load_workflow_template(self) -> Dict:
        """加载工作流模板"""
        import json
        import os
        
        json_file_path = os.path.join(os.getcwd(), settings.comfyui_text_to_image_workflow)
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            return workflow
        except FileNotFoundError:
            print(f"找不到工作流文件: {json_file_path}")
            # 返回一个简单的默认工作流模板
            return self._get_default_workflow()
        except json.JSONDecodeError:
            print(f"JSON文件格式错误: {json_file_path}")
            return None
    
    def _get_default_workflow(self) -> Dict:
        """
        返回一个基本的工作流模板
        如果找不到 AI_Image_API.json 文件时使用
        """
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "model.safetensors"}
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "default prompt", "clip": ["1", 1]}
            },
            "3": {
                "class_type": "CLIPTextEncode", 
                "inputs": {"text": "text, watermark", "clip": ["1", 1]}
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {"width": 512, "height": 512, "batch_size": 1}
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0]
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {"images": ["6", 0], "filename_prefix": "ComfyUI"}
            }
        }
    
    def _update_workflow_prompts(self, workflow: Dict, positive_prompt: str, negative_prompt: str,
                                model_name: str = None, width: int = None, height: int = None,
                                steps: int = None, cfg: int = None) -> Dict:
        """更新工作流中的提示词和参数"""
        if not workflow:
            return None
        
        # 更新正面提示词
        for node_id, node in workflow.items():
            if (node.get("class_type") == "CLIPTextEncode" and 
                "text" in node.get("inputs", {}) and 
                node["inputs"]["text"] != negative_prompt):
                workflow[node_id]["inputs"]["text"] = positive_prompt
                break
        
        # 更新负面提示词
        for node_id, node in workflow.items():
            if (node.get("class_type") == "CLIPTextEncode" and 
                "text" in node.get("inputs", {}) and 
                node["inputs"]["text"] != positive_prompt):
                workflow[node_id]["inputs"]["text"] = negative_prompt
                break
        
        # 更新模型
        if model_name:
            for node_id, node in workflow.items():
                if node.get("class_type") == "CheckpointLoaderSimple":
                    node["inputs"]["ckpt_name"] = model_name
                    break
        
        # 更新其他参数
        for node_id, node in workflow.items():
            if node.get("class_type") == "KSampler":
                inputs = node.get("inputs", {})
                inputs["seed"] = int(time.time() * 1000) % 1000000000  # 随机种子
                if steps is not None:
                    inputs["steps"] = steps
                if cfg is not None:
                    inputs["cfg"] = cfg
            elif node.get("class_type") == "EmptyLatentImage":
                inputs = node.get("inputs", {})
                if width is not None:
                    inputs["width"] = width
                if height is not None:
                    inputs["height"] = height
        
        return workflow
    
    def _wait_for_completion(self, server_address: str, prompt_id: str, task_id: str = None) -> Dict:
        """等待图像生成完成"""
        print("正在等待 ComfyUI 生成图像...")
        max_wait_time = settings.comfyui_timeout
        start_time = time.time()
        
        # 导入task_progress（需要在循环外访问）
        from app.routers.image_processing import task_progress
        
        progress_step = 0
        while time.time() - start_time < max_wait_time:
            try:
                # 查询队列状态
                queue_response = requests.get(f"http://{server_address}/queue", timeout=5)
                queue_data = queue_response.json()
                
                # 查询历史状态
                response = requests.get(f"http://{server_address}/history/{prompt_id}")
                history = response.json()
                
                if prompt_id in history:
                    # 任务完成
                    if task_id and task_id in task_progress:
                        task_progress[task_id].update({
                            "progress": 80,
                            "message": "图像生成完成，正在下载..."
                        })
                    return history[prompt_id]
                
                # 更新进度
                if task_id and task_id in task_progress:
                    # 检查任务在队列中的状态
                    running_queue = queue_data.get('queue_running', [])
                    pending_queue = queue_data.get('queue_pending', [])
                    
                    is_running = any(len(item) >= 2 and item[1] == prompt_id for item in running_queue)
                    
                    if is_running:
                        # 任务正在执行，递增进度
                        progress_step = min(progress_step + 2, 70)
                        task_progress[task_id].update({
                            "progress": 30 + progress_step,
                            "message": f"正在生成图像... ({progress_step}/70%)"
                        })
                    else:
                        # 检查是否在等待队列中
                        for i, item in enumerate(pending_queue):
                            if len(item) >= 2 and item[1] == prompt_id:
                                position = i + 1
                                total = len(pending_queue)
                                task_progress[task_id].update({
                                    "progress": 25,
                                    "message": f"排队中... ({position}/{total})"
                                })
                                break
                
            except Exception as e:
                print(f"检查任务状态时出错: {e}")
            
            time.sleep(1)
        
        raise Exception(f"ComfyUI 任务超时 ({max_wait_time}秒)")
    
    def _get_image(self, server_address: str, filename: str, subfolder: str, folder_type: str) -> bytes:
        """从服务器获取生成的图像"""
        from urllib.parse import urlencode
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urlencode(data)
        
        response = requests.get(f"http://{server_address}/view?{url_values}")
        return response.content
    
    def _fallback_generate_placeholder(self, prompt: str, width: int = 512, height: int = 512) -> Image.Image:
        """
        降级方案：生成一个包含提示词的占位图像
        当 ComfyUI 不可用时使用
        """
        from PIL import ImageDraw, ImageFont
        
        # 创建一个渐变背景
        img = Image.new('RGB', (width, height), color=(100, 150, 200))
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体，如果失败则使用默认字体
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # 添加文字
        text_lines = [
            "ComfyUI 暂时不可用",
            "这是占位图像",
            f"提示词: {prompt[:30]}..."
        ]
        
        y_offset = height // 2 - 40
        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill=(255, 255, 255), font=font)
            y_offset += 30
        
        return img
    
    def get_name(self) -> str:
        return "text_to_image"
    
    def get_description(self) -> str:
        return "使用 ComfyUI 根据文字描述生成图像"
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证文生图参数"""
        if not parameters:
            return False
        
        # 必须包含 prompt
        if 'prompt' not in parameters:
            return False
        
        # 验证可选参数的类型和范围
        width = parameters.get('width')
        if width and (not isinstance(width, int) or width < 64 or width > 2048):
            return False
        
        height = parameters.get('height')
        if height and (not isinstance(height, int) or height < 64 or height > 2048):
            return False
        
        steps = parameters.get('steps')
        if steps and (not isinstance(steps, int) or steps < 1 or steps > 100):
            return False
        
        cfg = parameters.get('cfg')
        if cfg and (not isinstance(cfg, (int, float)) or cfg < 1 or cfg > 30):
            return False
        
        return True

class CreativeUpscaleProcessor(ImageProcessor):
    """
    ComfyUI 创意放大修复处理器
    
    使用ComfyUI进行图片的创意放大和修复，参数固定，只需要输入图片
    """
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None, task_id: str = None) -> Image.Image:
        """
        使用 ComfyUI 进行创意放大修复
        
        Args:
            image: 输入图像
            parameters: 处理参数（此处理器参数固定）
            task_id: 任务ID，用于进度跟踪
        
        Returns:
            处理后的图像
        """
        try:
            # 调用 ComfyUI API
            image_data = self._call_comfyui_upscale_api(image, task_id)
            
            # 将图像数据转换为 PIL Image
            return Image.open(io.BytesIO(image_data))
            
        except Exception as e:
            print(f"ComfyUI 创意放大API调用失败: {e}")
            # 降级方案：使用简单的放大
            return self._fallback_upscale(image)
    
    def _call_comfyui_upscale_api(self, image: Image.Image, task_id: str = None) -> bytes:
        """
        调用 ComfyUI API 进行创意放大
        """
        import json
        import uuid
        import tempfile
        import os
        from urllib.parse import urlencode
        
        server_address = settings.comfyui_server_address
        client_id = str(uuid.uuid4())
        
        # 1. 保存输入图像到临时文件
        temp_image_path = self._save_temp_image(image)
        
        try:
            # 2. 上传图像到ComfyUI服务器
            uploaded_filename = self._upload_image_to_comfyui(temp_image_path, server_address)
            
            # 3. 加载放大工作流模板
            workflow = self._load_upscale_workflow_template()
            if not workflow:
                raise Exception("无法加载 ComfyUI 放大工作流模板")
            
            # 4. 更新工作流参数（使用上传后的文件名）
            workflow = self._update_upscale_workflow_with_uploaded_image(workflow, uploaded_filename)
            
            # 5. 提交到队列
            prompt_data = {"prompt": workflow, "client_id": client_id}
            data = json.dumps(prompt_data).encode('utf-8')
            
            response = requests.post(
                f"http://{server_address}/prompt", 
                data=data,
                timeout=settings.comfyui_timeout
            )
            result = response.json()
            prompt_id = result['prompt_id']
            
            print(f"ComfyUI 放大任务ID: {prompt_id}")
            
            # 6. 等待完成
            history = self._wait_for_completion(server_address, prompt_id, task_id)
            
            # 7. 获取生成的图像（参考示例代码，检查多种输出键名）
            for node_id in history['outputs']:
                node_output = history['outputs'][node_id]
                print(f"检查节点 {node_id}: {node_output}")
                
                # 检查多种可能的图像键名，优先使用b_images（处理后图像）
                image_keys = ['b_images', 'images']
                for key in image_keys:
                    if key in node_output:
                        for image_info in node_output[key]:
                            print(f"找到图像({key}): {image_info}")
                            image_data = self._get_image(
                                server_address, image_info['filename'], 
                                image_info['subfolder'], image_info['type']
                            )
                            return image_data
            
            raise Exception("未能从 ComfyUI 获取放大后的图像")
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
    
    def _upload_image_to_comfyui(self, image_path: str, server_address: str) -> str:
        """上传图像到ComfyUI服务器"""
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"http://{server_address}/upload/image", files=files)
            if response.status_code == 200:
                result = response.json()
                return result['name']  # 返回上传后的文件名
            else:
                raise Exception(f"图像上传失败: {response.status_code}")
    
    def _update_upscale_workflow_with_uploaded_image(self, workflow: Dict, uploaded_filename: str) -> Dict:
        """使用上传后的文件名更新工作流"""
        if not workflow:
            return None
        
        # 直接在工作流字典中查找LoadImage节点
        for node_id, node in workflow.items():
            if node.get("class_type") == "LoadImage":
                # 更新LoadImage节点的输入图像
                if "inputs" not in node:
                    node["inputs"] = {}
                node["inputs"]["image"] = uploaded_filename
                print(f"更新LoadImage节点 {node_id} 的图像路径为: {uploaded_filename}")
                break
        
        return workflow
    
    def _save_temp_image(self, image: Image.Image) -> str:
        """保存图像到指定目录"""
        import tempfile
        import os
        import uuid
        
        # 生成唯一文件名
        filename = f"input_{uuid.uuid4().hex[:8]}.png"
        
        # 使用配置的目录
        input_dir = settings.comfyui_input_dir
        
        # 确保目录存在
        os.makedirs(input_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(input_dir, filename)
        image.save(file_path, format='PNG')
        
        return file_path
    
    def _load_upscale_workflow_template(self) -> Dict:
        """加载放大工作流模板"""
        import json
        import os
        
        json_file_path = os.path.join(os.getcwd(), settings.comfyui_upscale_workflow)
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                workflow = json.load(f)
            return workflow
        except FileNotFoundError:
            print(f"找不到放大工作流文件: {json_file_path}")
            # 返回一个简单的默认放大工作流模板
            return self._get_default_upscale_workflow()
        except json.JSONDecodeError:
            print(f"JSON文件格式错误: {json_file_path}")
            return self._get_default_upscale_workflow()
    
    def _get_default_upscale_workflow(self) -> Dict:
        """
        返回一个基本的放大工作流模板
        如果找不到放大工作流文件时使用
        """
        return {
            "1": {
                "class_type": "LoadImage",
                "inputs": {"image": "input.png"}
            },
            "2": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "model.safetensors"}
            },
            "3": {
                "class_type": "VAEDecode",
                "inputs": {"samples": ["7", 0], "vae": ["2", 2]}
            },
            "4": {
                "class_type": "VAEEncode",
                "inputs": {"pixels": ["1", 0], "vae": ["2", 2]}
            },
            "5": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "masterpiece, best quality, highres", "clip": ["2", 1]}
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "text, watermark, blurry", "clip": ["2", 1]}
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 8,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 0.35,
                    "model": ["2", 0],
                    "positive": ["5", 0],
                    "negative": ["6", 0],
                    "latent_image": ["4", 0]
                }
            },
            "8": {
                "class_type": "SaveImage",
                "inputs": {"images": ["3", 0], "filename_prefix": "upscaled"}
            }
        }
    
    def _update_upscale_workflow(self, workflow: Dict, image_path: str) -> Dict:
        """更新放大工作流中的图像路径"""
        if not workflow:
            return None
        
        import os
        
        # 获取图像文件名
        image_filename = os.path.basename(image_path)
        
        # 参考文生图API的方式，直接在工作流字典中查找LoadImage节点
        for node_id, node in workflow.items():
            if node.get("class_type") == "LoadImage":
                # 更新LoadImage节点的输入图像
                # LoadImage节点的输入通常是 "image" 参数
                if "inputs" not in node:
                    node["inputs"] = {}
                node["inputs"]["image"] = image_filename
                print(f"更新LoadImage节点 {node_id} 的图像路径为: {image_filename}")
                break
        
        return workflow
    
    def _wait_for_completion(self, server_address: str, prompt_id: str, task_id: str = None) -> Dict:
        """等待图像生成完成"""
        print("正在等待 ComfyUI 放大处理...")
        max_wait_time = settings.comfyui_timeout
        start_time = time.time()
        
        # 导入task_progress（需要在循环外访问）
        from app.routers.image_processing import task_progress
        
        count = 0
        while time.time() - start_time < max_wait_time:
            try:
                # 查询历史状态
                response = requests.get(f"http://{server_address}/history/{prompt_id}")
                history = response.json()
                
                if prompt_id in history:
                    # 任务完成
                    if task_id and task_id in task_progress:
                        task_progress[task_id].update({
                            "progress": 80,
                            "message": "放大处理完成，正在下载..."
                        })
                    print("✅ 放大处理完成！")
                    return history[prompt_id]
                
                count += 1
                # 更新进度
                if task_id and task_id in task_progress:
                    progress = min(30 + (count * 2), 70)
                    task_progress[task_id].update({
                        "progress": progress,
                        "message": f"正在放大处理... ({count}秒)"
                    })
                
                if count % 5 == 0:  # 每5秒打印一次状态
                    print(f"⏳ 等待中... ({count}秒)")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"检查任务状态时出错: {e}")
                time.sleep(2)
        
        raise Exception(f"ComfyUI 放大任务超时 ({max_wait_time}秒)")
    
    def _get_image(self, server_address: str, filename: str, subfolder: str, folder_type: str) -> bytes:
        """从服务器获取生成的图像"""
        from urllib.parse import urlencode
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urlencode(data)
        
        response = requests.get(f"http://{server_address}/view?{url_values}")
        return response.content
    
    def _fallback_upscale(self, image: Image.Image) -> Image.Image:
        """
        降级方案：简单的4倍放大
        """
        width, height = image.size
        new_size = (width * 4, height * 4)
        
        # 使用双三次插值进行放大
        upscaled = image.resize(new_size, Image.LANCZOS)
        return upscaled
    
    def get_name(self) -> str:
        return "creative_upscale"
    
    def get_description(self) -> str:
        return "使用 ComfyUI 进行创意放大修复，提升图像质量和细节"
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """创意放大不需要额外参数验证"""
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
        # 移除旧的外部API超分处理器
        # self.register_processor(UpscaleProcessor())  
        self.register_processor(TextToImageProcessor())
        self.register_processor(CreativeUpscaleProcessor())
    
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
        parameters: Dict[str, Any] = None,
        task_id: str = None
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
        processed_image = processor.process(image, parameters or {}, task_id)
        
        # 保存处理后的图像
        output_buffer = io.BytesIO()
        processed_image.save(output_buffer, format='PNG')
        output_data = output_buffer.getvalue()
        
        processing_time = time.time() - start_time
        
        return output_data, processing_time

# 全局服务实例
image_processing_service = ImageProcessingService()