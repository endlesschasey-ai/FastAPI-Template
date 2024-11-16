# middlewares/exception.py
import sys
import time
import traceback
from typing import Callable
from datetime import datetime
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError as PydanticValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.exceptions.base import AppException
from app.schemas.error import ErrorResponse
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger()

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    全局异常处理中间件
    
    功能：
    1. 捕获并处理所有异常
    2. 统一错误响应格式
    3. 错误日志记录
    4. 开发环境堆栈追踪
    
    使用方法：
    ```python
    from app.middlewares.exception import ExceptionHandlerMiddleware
    
    app = FastAPI()
    app.add_middleware(ExceptionHandlerMiddleware)
    ```
    """
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        try:
            return await call_next(request)
            
        except AppException as e:
            # 处理应用自定义异常
            return self._handle_app_exception(e, request)
            
        except PydanticValidationError as e:
            # 处理Pydantic验证异常
            return self._handle_validation_error(e, request)
            
        except SQLAlchemyError as e:
            # 处理数据库异常
            return self._handle_database_error(e, request)
            
        except Exception as e:
            # 处理其他未预期的异常
            return self._handle_unknown_error(e, request)
    
    def _handle_app_exception(
        self,
        exc: AppException,
        request: Request
    ) -> JSONResponse:
        """处理应用自定义异常"""
        error_response = ErrorResponse(
            error_code=exc.error_code,
            message=exc.detail,
            details=exc.details,
            trace_id=getattr(request.state, "request_id", None)
        )
        
        # 记录错误日志
        logger.error(
            f"Application error: {exc.detail}",
            extra={
                "error_code": exc.error_code,
                "path": request.url.path,
                "method": request.method,
                "details": exc.details
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump()
        )
    
    def _handle_validation_error(
        self,
        exc: PydanticValidationError,
        request: Request
    ) -> JSONResponse:
        """处理Pydantic验证异常"""
        error_response = ErrorResponse(
            error_code=4000,
            message="Validation error",
            details=exc.errors(),
            trace_id=getattr(request.state, "request_id", None)
        )
        
        logger.warning(
            "Validation error",
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )
        
        return JSONResponse(
            status_code=400,
            content=error_response.model_dump()
        )
    
    def _handle_database_error(
        self,
        exc: SQLAlchemyError,
        request: Request
    ) -> JSONResponse:
        """处理数据库异常"""
        error_response = ErrorResponse(
            error_code=5000,
            message="Database error occurred",
            details=str(exc) if settings.DEBUG else None,
            trace_id=getattr(request.state, "request_id", None)
        )
        
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error": str(exc)
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
    
    def _handle_unknown_error(
        self,
        exc: Exception,
        request: Request
    ) -> JSONResponse:
        """处理未知异常"""
        error_response = ErrorResponse(
            error_code=5001,
            message="Internal server error",
            trace_id=getattr(request.state, "request_id", None)
        )
        
        # 在开发环境下添加堆栈信息
        if settings.DEBUG:
            error_response.details = {
                "error": str(exc),
                "traceback": traceback.format_exception(
                    type(exc),
                    exc,
                    exc.__traceback__
                )
            }
        
        # 记录错误日志
        logger.error(
            f"Unhandled error: {str(exc)}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "error_type": type(exc).__name__
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """
    错误日志记录中间件
    
    功能：
    1. 记录所有错误信息
    2. 错误统计和监控
    3. 错误告警通知
    
    使用方法：
    ```python
    from app.middlewares.exception import ErrorLoggingMiddleware
    
    app = FastAPI()
    app.add_middleware(
        ErrorLoggingMiddleware,
        alert_threshold=10  # 错误数超过阈值时发送告警
    )
    ```
    """
    def __init__(
        self,
        app: ASGIApp,
        alert_threshold: int = 10,
        alert_interval: int = 60
    ) -> None:
        super().__init__(app)
        self.alert_threshold = alert_threshold
        self.alert_interval = alert_interval
        self.error_count = 0
        self.last_alert_time = 0
    
    async def _should_send_alert(self) -> bool:
        """检查是否需要发送告警"""
        current_time = int(time.time())
        if (self.error_count >= self.alert_threshold and 
            current_time - self.last_alert_time > self.alert_interval):
            self.last_alert_time = current_time
            self.error_count = 0
            return True
        return False
    
    async def _send_alert(self, error_info: dict) -> None:
        """发送错误告警
        这里可以集成告警系统，如邮件、钉钉、企业微信等
        """
        logger.critical(
            "Error alert triggered",
            extra={
                "error_count": self.error_count,
                "threshold": self.alert_threshold,
                "error_info": error_info
            }
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        try:
            return await call_next(request)
            
        except Exception as e:
            # 增加错误计数
            self.error_count += 1
            
            # 构建错误信息
            error_info = {
                "path": request.url.path,
                "method": request.method,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
            # 检查是否需要告警
            if await self._should_send_alert():
                await self._send_alert(error_info)
            
            raise

# 使用示例
"""
from fastapi import FastAPI
from app.middlewares.exception import (
    ExceptionHandlerMiddleware,
    ErrorLoggingMiddleware
)

app = FastAPI()

# 添加中间件（注意顺序）
app.add_middleware(ErrorLoggingMiddleware, alert_threshold=10)
app.add_middleware(ExceptionHandlerMiddleware)

# 使用自定义异常
@app.get("/test-error")
async def test_error():
    raise AuthenticationError("Invalid token")

@app.get("/test-business-error")
async def test_business_error():
    raise BusinessError(
        message="Insufficient balance",
        error_code=4101,
        details={"balance": 0, "required": 100}
    )
"""