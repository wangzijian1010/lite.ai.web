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
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    class Config:
        env_file = ".env"

settings = Settings()