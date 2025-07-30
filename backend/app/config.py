import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # PostgreSQL数据库连接配置
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # 数据库连接池配置
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    db_pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    db_pool_pre_ping: bool = True
    
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: str = "jpg,jpeg,png,webp"
    
    # 邮箱配置
    smtp_host: str = "smtp.qq.com"  # QQ邮箱SMTP服务器
    smtp_port: int = 587
    smtp_username: str = ""  # 发送邮箱地址
    smtp_password: str = ""  # 邮箱授权码
    smtp_from_email: str = ""  # 发件人邮箱（通常与smtp_username相同）
    smtp_from_name: str = "吉卜力AI"
    
    # 验证码配置
    verification_code_expire_minutes: int = 5  # 验证码5分钟过期
    verification_code_length: int = 6  # 6位验证码
    max_verification_attempts: int = 3  # 最大验证次数
    email_send_cooldown_seconds: int = 60  # 邮箱发送冷却时间（防刷）
    
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
        env_file = [".env", ".env.production"]

settings = Settings()