from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"
    secret_key: str = "your-secret-key-here"
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = "jpg,jpeg,png,webp"
    
    # 超分 API 配置
    upscale_api_url: str = "https://api.example.com/upscale"
    upscale_api_key: str = "your-api-key-here"
    upscale_api_timeout: int = 30
    
    # ComfyUI 配置
    comfyui_server_address: str = "127.0.0.1:8188"
    comfyui_workflow_json: str = "workflow/text_to_image_workflow.json"  # 保留兼容性
    comfyui_text_to_image_workflow: str = "workflow/text_to_image_workflow.json"
    comfyui_upscale_workflow: str = "workflow/upscale_workflow.json"
    comfyui_input_dir: str = "./comfyui_temp"  # ComfyUI输入文件目录
    comfyui_timeout: int = 120
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()