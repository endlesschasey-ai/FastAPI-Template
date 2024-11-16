# schemas/token.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Token(BaseModel):
    """
    Token响应模型
    """
    access_token: str = Field(
        ...,
        description="访问令牌",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx"
    )
    refresh_token: str = Field(
        ..., 
        description="刷新令牌",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.yyy"
    )
    token_type: str = Field(
        default="bearer",
        description="令牌类型",
        example="bearer"
    )
    expires_in: int = Field(
        ...,
        description="访问令牌过期时间(秒)",
        example=3600
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.yyy", 
                "token_type": "bearer",
                "expires_in": 3600
            }
        }
    )

class TokenPayload(BaseModel):
    """
    Token载荷模型
    """
    sub: str | int = Field(
        ...,
        description="主题(通常是用户ID)",
        example="123"
    )
    exp: datetime = Field(
        ...,
        description="过期时间",
        example="2024-12-31T23:59:59"
    )
    iat: Optional[datetime] = Field(
        default=None,
        description="签发时间",
        example="2024-01-01T00:00:00"
    )
    type: str = Field(
        default="access",
        description="令牌类型(access或refresh)",
        example="access"
    )
    jti: Optional[str] = Field(
        default=None,
        description="JWT ID",
        example="unique-jwt-id-123"
    )
    
    model_config = ConfigDict(json_encoders={
        datetime: lambda v: v.timestamp()
    })

class RefreshToken(BaseModel):
    """
    刷新令牌请求
    """
    refresh_token: str = Field(
        ...,
        description="刷新令牌",
        min_length=1,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.yyy"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.yyy"
            }
        }
    )

class TokenBlacklist(BaseModel):
    """
    Token黑名单模型
    """
    jti: str = Field(
        ...,
        description="JWT ID",
        example="unique-jwt-id-123"
    )
    exp: datetime = Field(
        ...,
        description="过期时间",
        example="2024-12-31T23:59:59"
    )
    type: str = Field(
        ...,
        description="令牌类型",
        example="access"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "jti": "unique-jwt-id-123",
                "exp": "2024-12-31T23:59:59",
                "type": "access",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    )

class TokenMetadata(BaseModel):
    """
    Token元数据模型,用于存储额外的token信息
    """
    user_id: int = Field(
        ...,
        description="用户ID",
        example=123
    )
    device_id: Optional[str] = Field(
        default=None,
        description="设备ID",
        example="device-123"
    )
    ip_address: Optional[str] = Field(
        default=None,
        description="IP地址",
        example="192.168.1.1"
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="User Agent",
        example="Mozilla/5.0 ..."
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间"
    )
    
    model_config = ConfigDict(from_attributes=True)