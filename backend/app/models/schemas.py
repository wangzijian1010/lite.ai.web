from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from enum import Enum
from datetime import datetime

class ProcessingType(str, Enum):
    GRAYSCALE = "grayscale"
    GHIBLI_STYLE = "ghibli_style"
    UPSCALE = "upscale"
    TEXT_TO_IMAGE = "text_to_image"
    CREATIVE_UPSCALE = "creative_upscale"
    BLUR = "blur"
    EDGE_DETECTION = "edge_detection"

class ImageProcessRequest(BaseModel):
    processing_type: ProcessingType
    parameters: Optional[Dict[str, Any]] = {}

class ImageProcessResponse(BaseModel):
    success: bool
    message: str
    processed_image_url: Optional[str] = None
    processing_type: str
    processing_time: float

class TextToImageAsyncResponse(BaseModel):
    success: bool
    message: str
    task_id: str
    prompt_id: Optional[str] = None
    estimated_time: Optional[int] = None

class ProgressResponse(BaseModel):
    success: bool
    task_id: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    progress: int  # 0-100
    message: str
    result_url: Optional[str] = None
    error: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None

# 用户相关模型
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    verification_code: str  # 邮箱验证码

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 邮箱验证相关
class SendVerificationCodeRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class SendVerificationCodeResponse(BaseModel):
    success: bool
    message: str
    cooldown_seconds: Optional[int] = None