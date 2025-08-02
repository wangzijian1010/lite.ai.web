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
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.qq.com")  # QQ邮箱SMTP服务器
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")  # 发送邮箱地址
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")  # 邮箱授权码
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "")  # 发件人邮箱（通常与smtp_username相同）
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "吉卜力AI")
    
    # 验证码配置
    verification_code_expire_minutes: int = int(os.getenv("VERIFICATION_CODE_EXPIRE_MINUTES", "5"))  # 验证码5分钟过期
    verification_code_length: int = int(os.getenv("VERIFICATION_CODE_LENGTH", "6"))  # 6位验证码
    max_verification_attempts: int = int(os.getenv("MAX_VERIFICATION_ATTEMPTS", "3"))  # 最大验证次数
    email_send_cooldown_seconds: int = int(os.getenv("EMAIL_SEND_COOLDOWN_SECONDS", "60"))  # 邮箱发送冷却时间（防刷）
    
    # 超分 API 配置
    upscale_api_url: str = "https://api.example.com/upscale"
    upscale_api_key: str = "your-api-key-here"
    upscale_api_timeout: int = 30
    
    # ComfyUI 配置
    comfyui_server_address: str = os.getenv("COMFYUI_SERVER_ADDRESS", "127.0.0.1:8188")
    comfyui_token: str = os.getenv("COMFYUI_TOKEN", "")
    comfyui_workflow_json: str = os.getenv("COMFYUI_TEXT_TO_IMAGE_WORKFLOW", "workflow/text_to_image_workflow.json")  # 保留兼容性
    comfyui_text_to_image_workflow: str = os.getenv("COMFYUI_TEXT_TO_IMAGE_WORKFLOW", "workflow/text_to_image_workflow.json")
    comfyui_upscale_workflow: str = os.getenv("COMFYUI_UPSCALE_WORKFLOW", "workflow/upscale_0801.json")
    comfyui_input_dir: str = os.getenv("COMFYUI_INPUT_DIR", "./comfyui_temp")  # ComfyUI输入文件目录
    comfyui_timeout: int = int(os.getenv("COMFYUI_TIMEOUT", "120"))
    
    # Redis配置
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_password: str = os.getenv("REDIS_PASSWORD", "")
    redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    class Config:
        env_file = [".env", ".env.production"]

settings = Settings()