# 外部 API 集成指南

## 如何添加图片超分放大功能 - 完整步骤

本文档详细记录了如何在现有系统中添加图片超分放大功能，作为外部 API 调用的示例。

### 第一步：添加配置文件

#### 1.1 更新环境变量文件 (.env)
```bash
# 在 .env 文件中添加超分 API 配置
UPSCALE_API_URL=https://api.example.com/upscale
UPSCALE_API_KEY=your-api-key-here
UPSCALE_API_TIMEOUT=30
```

#### 1.2 更新配置类 (app/config.py)
```python
class Settings(BaseSettings):
    # 现有配置...
    
    # 新增：超分 API 配置
    upscale_api_url: str = "https://api.example.com/upscale"
    upscale_api_key: str = "your-api-key-here"
    upscale_api_timeout: int = 30
```

### 第二步：更新数据模型

#### 2.1 添加处理类型枚举 (app/models/schemas.py)
```python
class ProcessingType(str, Enum):
    GRAYSCALE = "grayscale"
    GHIBLI_STYLE = "ghibli_style"
    UPSCALE = "upscale"  # 新增
    # ... 其他类型
```

### 第三步：创建处理器类

#### 3.1 实现 UpscaleProcessor (app/services/image_processing.py)
```python
class UpscaleProcessor(ImageProcessor):
    """图片超分放大处理器"""
    
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        scale_factor = parameters.get('scale_factor', 2) if parameters else 2
        model = parameters.get('model', 'real-esrgan') if parameters else 'real-esrgan'
        
        try:
            # 调用外部 API
            return self._call_upscale_api_sync(image, scale_factor, model)
        except Exception as e:
            print(f"外部API调用失败: {e}")
            # 降级方案：使用简单插值放大
            return self._fallback_upscale(image, scale_factor)
    
    def _call_upscale_api_sync(self, image: Image.Image, scale_factor: int, model: str) -> Image.Image:
        """同步调用外部超分API"""
        # 1. 图像转 base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 2. 准备请求数据
        api_data = {
            "image": image_base64,
            "scale_factor": scale_factor,
            "model": model,
            "format": "png"
        }
        
        # 3. 设置请求头
        headers = {
            "Authorization": f"Bearer {settings.upscale_api_key}",
            "Content-Type": "application/json"
        }
        
        # 4. 发送请求
        response = requests.post(
            settings.upscale_api_url,
            json=api_data,
            headers=headers,
            timeout=settings.upscale_api_timeout
        )
        
        # 5. 处理响应
        if response.status_code == 200:
            result_data = response.json()
            if result_data.get("success"):
                result_image_base64 = result_data.get("result_image")
                result_image_data = base64.b64decode(result_image_base64)
                return Image.open(io.BytesIO(result_image_data))
            else:
                raise Exception(f"API返回错误: {result_data.get('message')}")
        else:
            raise Exception(f"API请求失败: HTTP {response.status_code}")
    
    def _fallback_upscale(self, image: Image.Image, scale_factor: int) -> Image.Image:
        """降级方案：简单插值放大"""
        width, height = image.size
        new_size = (width * scale_factor, height * scale_factor)
        return image.resize(new_size, Image.LANCZOS)
```

#### 3.2 注册新处理器
```python
def _register_default_processors(self):
    """注册默认的处理器"""
    self.register_processor(GrayscaleProcessor())
    self.register_processor(GhibliStyleProcessor())
    self.register_processor(UpscaleProcessor())  # 新增
```

### 第四步：更新前端

#### 4.1 添加新的 API 调用方法 (frontend/src/stores/ghibli.ts)
```typescript
async upscaleImage(file: File, scaleFactor: number = 2): Promise<string> {
  return this.processImage(file, 'upscale', { scale_factor: scaleFactor })
}
```

#### 4.2 更新UI选项 (frontend/src/views/Home.vue)
```vue
<button 
  @click="selectedProcessing = 'upscale'"
  :class="['processing-btn', { active: selectedProcessing === 'upscale' }]"
>
  🔍 AI超分放大
</button>
```

#### 4.3 更新处理逻辑
```typescript
if (selectedProcessing.value === 'upscale') {
  result = await ghibliStore.upscaleImage(file, 2) // 默认2倍放大
}
```

### 第五步：安装依赖

#### 5.1 更新 requirements.txt
```
requests>=2.31.0
aiohttp>=3.9.0  # 可选，用于异步调用
```

#### 5.2 安装依赖
```bash
pip install requests aiohttp
```

### 第六步：测试功能

#### 6.1 启动后端
```bash
cd backend
uvicorn app.main:app --reload
```

#### 6.2 访问 API 文档
打开 http://localhost:8000/docs 查看新增的处理器

#### 6.3 测试 API 调用
```bash
curl -X GET "http://localhost:8000/api/processors"
```

应该看到返回结果包含：
```json
{
  "success": true,
  "processors": {
    "grayscale": "将彩色图像转换为灰度图像",
    "ghibli_style": "将图像转换为吉卜力工作室风格（模拟实现）",
    "upscale": "使用AI超分技术放大图片，提升分辨率和清晰度"
  }
}
```

## 常见的外部 API 集成模式

### 模式1：简单的 REST API 调用
```python
def _call_simple_api(self, image_data, params):
    response = requests.post(
        "https://api.example.com/process",
        files={"image": image_data},
        data=params,
        headers={"Authorization": f"Bearer {api_key}"}
    )
    return response.json()
```

### 模式2：Base64 图像传输
```python
def _call_base64_api(self, image: Image.Image):
    # 图像转 base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # 发送请求
    response = requests.post(
        "https://api.example.com/process",
        json={"image": image_base64}
    )
    
    # 解析返回的 base64 图像
    result_base64 = response.json()["result_image"]
    result_data = base64.b64decode(result_base64)
    return Image.open(io.BytesIO(result_data))
```

### 模式3：异步处理（长时间任务）
```python
async def _call_async_api(self, image: Image.Image):
    # 1. 提交任务
    submit_response = await self._submit_task(image)
    task_id = submit_response["task_id"]
    
    # 2. 轮询任务状态
    while True:
        status_response = await self._check_task_status(task_id)
        if status_response["status"] == "completed":
            return await self._get_task_result(task_id)
        elif status_response["status"] == "failed":
            raise Exception("任务处理失败")
        
        await asyncio.sleep(2)  # 等待2秒后重试
```

## 更改 API 请求格式的步骤

当需要更改API请求格式时，只需要修改对应处理器类中的 `_call_*_api` 方法：

### 示例：更改请求格式
```python
# 原始格式
api_data = {
    "image": image_base64,
    "scale_factor": scale_factor
}

# 新格式 - 只需要修改这部分
api_data = {
    "input": {
        "image_data": image_base64,
        "parameters": {
            "scale": scale_factor,
            "model_type": model
        }
    },
    "output_format": "base64"
}
```

## 添加新功能的通用模板

```python
class YourNewProcessor(ImageProcessor):
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        try:
            # 调用外部 API
            return self._call_external_api(image, parameters)
        except Exception as e:
            print(f"外部API调用失败: {e}")
            # 提供降级方案
            return self._fallback_processing(image, parameters)
    
    def _call_external_api(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        # 1. 准备数据
        # 2. 发送请求  
        # 3. 处理响应
        # 4. 返回结果
        pass
    
    def _fallback_processing(self, image: Image.Image, parameters: Dict[str, Any]) -> Image.Image:
        # 当外部API不可用时的处理逻辑
        pass
    
    def get_name(self) -> str:
        return "your_processor_name"
    
    def get_description(self) -> str:
        return "您的处理器描述"
```

## 注意事项

1. **错误处理**：始终包含适当的异常处理和降级方案
2. **超时设置**：为外部API调用设置合理的超时时间
3. **API密钥安全**：使用环境变量存储敏感信息
4. **参数验证**：实现 `validate_parameters` 方法验证输入参数
5. **日志记录**：添加适当的日志记录便于调试
6. **速率限制**：考虑外部API的速率限制，必要时添加重试机制