from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class ProcessingType(str, Enum):
    GRAYSCALE = "grayscale"
    GHIBLI_STYLE = "ghibli_style"
    UPSCALE = "upscale"
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

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None