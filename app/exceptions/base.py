# exceptions/base.py
from typing import Any, Optional
from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

class AppException(HTTPException):
    """
    应用基础异常类
    
    属性:
        error_code: 错误码
        message: 错误消息
        details: 详细信息(可选)
    """
    def __init__(
        self,
        error_code: int,
        message: str,
        status_code: int = HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None
    ) -> None:
        self.error_code = error_code
        self.details = details
        super().__init__(status_code=status_code, detail=message)

class DatabaseError(AppException):
    """数据库错误"""
    def __init__(
        self,
        message: str = "数据库操作失败",
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=5000,
            message=message,
            status_code=500,
            details=details
        )

class ValidationError(AppException):
    """数据验证错误"""
    def __init__(
        self,
        message: str = "数据验证失败",
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=4000,
            message=message,
            status_code=400,
            details=details
        )

class AuthenticationError(AppException):
    """认证错误"""
    def __init__(
        self,
        message: str = "身份验证失败",
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=4001,
            message=message,
            status_code=401,
            details=details
        )

class AuthorizationError(AppException):
    """授权错误"""
    def __init__(
        self,
        message: str = "权限不足",
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=4003,
            message=message,
            status_code=403,
            details=details
        )

class NotFoundError(AppException):
    """资源不存在错误"""
    def __init__(
        self,
        message: str = "未找到请求的资源",
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=4004,
            message=message,
            status_code=404,
            details=details
        )

class BusinessError(AppException):
    """业务逻辑错误"""
    def __init__(
        self,
        message: str,
        error_code: int = 4100,
        details: Optional[Any] = None
    ):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=400,
            details=details
        )