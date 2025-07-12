# 后端开发指南

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 主应用
│   ├── config.py            # 配置管理
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic 数据模型
│   ├── routers/
│   │   ├── __init__.py
│   │   └── image_processing.py  # API 路由
│   ├── services/
│   │   ├── __init__.py
│   │   └── image_processing.py  # 核心业务逻辑
│   └── utils/
│       ├── __init__.py
│       └── file_utils.py    # 工具函数
├── requirements.txt         # 依赖包
└── .env                    # 环境变量
```

## 如何添加新的图像处理功能

### 1. 创建新的处理器

在 `app/services/image_processing.py` 中添加新的处理器类：

```python
class YourNewProcessor(ImageProcessor):
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        # 实现您的图像处理逻辑
        # 例如：调用外部 AI API
        
        # 示例：边缘检测
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        edges = cv2.Canny(cv_image, 100, 200)
        return Image.fromarray(edges)
    
    def get_name(self) -> str:
        return "your_processor_name"
    
    def get_description(self) -> str:
        return "您的处理器描述"
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        # 可选：添加参数验证逻辑
        return True
```

### 2. 注册新处理器

在 `ImageProcessingService.__init__()` 方法中注册：

```python
def _register_default_processors(self):
    self.register_processor(GrayscaleProcessor())
    self.register_processor(GhibliStyleProcessor())
    self.register_processor(YourNewProcessor())  # 添加这行
```

### 3. 更新数据模型（可选）

如果需要新的处理类型，在 `app/models/schemas.py` 中更新枚举：

```python
class ProcessingType(str, Enum):
    GRAYSCALE = "grayscale"
    GHIBLI_STYLE = "ghibli_style"
    YOUR_NEW_TYPE = "your_processor_name"  # 添加新类型
```

### 4. 测试新功能

启动服务器后，访问 `/api/processors` 端点查看所有可用处理器。

## API 调用示例

### 处理图像
```bash
curl -X POST "http://localhost:8000/api/process" \
     -F "file=@your_image.jpg" \
     -F "processing_type=grayscale"
```

### 带参数的处理
```bash
curl -X POST "http://localhost:8000/api/process" \
     -F "file=@your_image.jpg" \
     -F "processing_type=your_processor_name" \
     -F 'parameters={"param1": "value1", "param2": 123}'
```

### 获取可用处理器
```bash
curl "http://localhost:8000/api/processors"
```

## 外部 AI API 集成示例

```python
class ExternalAIProcessor(ImageProcessor):
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        # 将图像转换为 base64
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 调用外部 API
        response = requests.post(
            "https://api.example.com/process",
            json={
                "image": image_base64,
                "style": "ghibli",
                "parameters": parameters
            },
            headers={"Authorization": "Bearer YOUR_API_KEY"}
        )
        
        # 处理响应
        result_data = response.json()
        processed_image_data = base64.b64decode(result_data["processed_image"])
        
        return Image.open(io.BytesIO(processed_image_data))
```

## 启动开发服务器

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API 文档将在 http://localhost:8000/docs 可用。