# schemas/error.py
from typing import Any, Optional
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """错误响应模型"""
    error_code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[Any] = Field(None, description="详细信息")
    trace_id: Optional[str] = Field(None, description="追踪ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error_code": 4001,
                "message": "Authentication failed",
                "details": None,
                "trace_id": "1234567890"
            }
        }