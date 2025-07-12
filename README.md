# 🎨 AI 图像处理平台

> 一个基于 Vue.js + FastAPI 的现代化 AI 图像处理 Web 应用

[![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?style=for-the-badge&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org/)

## 🚀 项目概述

这是一个集成了多种 AI 能力的图像处理平台，提供了从基础图像操作到高级 AI 风格转换的全方位解决方案。通过现代化的前后端分离架构，为用户提供流畅的图像处理体验。

### ✨ 核心特性

- 🎯 **多样化 AI 处理器**：支持[Lite.ai.Toolkit](https://github.com/xlite-dev/lite.ai.toolkit)上大部分算法、宫崎骏风格转换等多种图像处理算法,以及一些 ComfyUI 的有趣的工作流
- 🔌 **可扩展架构**：插件化的处理器设计，轻松集成第三方 AI API
- ⚡ **异步处理**：基于 FastAPI 的高性能异步图像处理
- 🎨 **现代化 UI**：使用 Vue 3 + Composition API 构建的响应式界面
- 📡 **RESTful API**：标准化的 API 设计，支持自动文档生成
- 🛡️ **类型安全**：前端 TypeScript + 后端 Pydantic 双重类型保障

## 🏗️ 技术架构

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Vue.js 前端    │ ←──────────────────→ │  FastAPI 后端   │
│                 │                      │                 │
│ • Composition API│                      │ • 异步处理       │
│ • TypeScript    │                      │ • Pydantic 验证  │
│ • Vite 构建     │                      │ • SQLAlchemy ORM│
│ • Pinia 状态管理 │                      │ • AI 处理器插件  │
└─────────────────┘                      └─────────────────┘
                                                   │
                                                   ▼
                                         ┌─────────────────┐
                                         │   AI 处理层     │
                                         │                 │
                                         │ • OpenCV        │
                                         │ • PIL/Pillow    │
                                         │ • 外部 AI API   │
                                         │ • 自定义算法     │
                                         └─────────────────┘
```

## 📁 项目结构

```
my-app/
├── 📁 frontend/                 # Vue.js 前端应用
│   ├── 📁 src/
│   │   ├── 📁 components/       # 可复用组件
│   │   ├── 📁 views/           # 页面视图
│   │   ├── 📁 stores/          # Pinia 状态管理
│   │   ├── 📁 types/           # TypeScript 类型定义
│   │   ├── 📁 utils/           # 工具函数
│   │   └── 📄 main.ts          # 应用入口
│   ├── 📄 package.json
│   └── 📄 vite.config.ts
├── 📁 backend/                  # FastAPI 后端应用
│   ├── 📁 app/
│   │   ├── 📄 main.py          # FastAPI 主应用
│   │   ├── 📁 models/          # 数据模型
│   │   ├── 📁 routers/         # API 路由
│   │   ├── 📁 services/        # 业务逻辑层
│   │   └── 📁 utils/           # 工具模块
│   ├── 📄 requirements.txt
│   └── 📄 .env                 # 环境配置
├── 📄 .gitignore
└── 📄 README.md
```

## 🛠️ AI 处理器架构

### 处理器接口设计

```python
class ImageProcessor(ABC):
    @abstractmethod
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        """处理图像的核心方法"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取处理器名称"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """获取处理器描述"""
        pass
```

### 内置处理器

- **🎨 GrayscaleProcessor**: 高质量灰度转换
- **🌸 GhibliStyleProcessor**: 宫崎骏动画风格转换
- **🔧 CustomProcessor**: 自定义参数化处理

### 外部 AI 集成示例

```python
class AIUpscaleProcessor(ImageProcessor):
    """AI 图像超分辨率处理器"""
    
    async def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        # 调用第三方 AI API
        upscaled_image = await self.call_ai_api(image, parameters)
        return upscaled_image
```

## 🚀 快速开始

### 环境要求

- **Node.js**: >= 16.0
- **Python**: >= 3.9
- **npm/yarn**: 包管理器

### 1. 克隆项目

```bash
git clone <repository-url>
cd my-app
```

### 2. 启动后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端应用

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- **前端应用**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **API 交互**: http://localhost:8000/redoc

## 📖 API 使用指南

### 图像处理端点

```http
POST /api/process
Content-Type: multipart/form-data

file: <image-file>
processing_type: "ghibli_style"
parameters: {"intensity": 0.8}
```

### 获取可用处理器

```http
GET /api/processors
```

响应示例：
```json
{
  "processors": [
    {
      "name": "grayscale",
      "description": "将图像转换为灰度",
      "parameters": []
    },
    {
      "name": "ghibli_style",
      "description": "宫崎骏动画风格转换",
      "parameters": ["intensity"]
    }
  ]
}
```

## 🔧 开发指南

### 添加新的 AI 处理器

1. **创建处理器类**

```python
# backend/app/services/processors/your_processor.py
class YourAIProcessor(ImageProcessor):
    def process(self, image: Image.Image, parameters: Dict[str, Any] = None) -> Image.Image:
        # 实现你的 AI 处理逻辑
        processed_image = your_ai_function(image, **parameters)
        return processed_image
    
    def get_name(self) -> str:
        return "your_ai_processor"
    
    def get_description(self) -> str:
        return "你的 AI 处理器描述"
```

2. **注册处理器**

```python
# backend/app/services/image_processing.py
def _register_default_processors(self):
    self.register_processor(YourAIProcessor())
```

3. **更新前端类型**

```typescript
// frontend/src/types/processing.ts
export type ProcessingType = 'grayscale' | 'ghibli_style' | 'your_ai_processor'
```

### 环境配置

```bash
# backend/.env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-super-secret-key
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# AI API 配置
OPENAI_API_KEY=your-openai-key
STABILITY_AI_KEY=your-stability-key
REPLICATE_API_TOKEN=your-replicate-token
```

## 🎯 性能优化

- **图像缓存**: Redis 缓存处理结果
- **异步处理**: 支持批量图像处理
- **流式传输**: 大文件分块上传下载
- **CDN 集成**: 静态资源加速

## 🔮 未来规划

- [ ] 🤖 集成更多 AI 模型 (Stable Diffusion, DALL-E)
- [ ] 🎬 视频处理支持
- [ ] 👥 用户系统和处理历史
- [ ] 📊 处理结果分析和对比
- [ ] 🌐 多语言支持
- [ ] 📱 移动端适配

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 📧 Email: ryanadkins512@gmail.com

---

⭐ 如果这个项目对你有帮助，请考虑给个 Star！