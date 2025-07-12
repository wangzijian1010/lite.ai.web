from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

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