# middlewares/logging.py
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger()

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    请求日志中间件
    
    功能：
    1. 记录详细的请求信息
    2. 记录响应信息
    3. 记录性能指标
    4. 支持敏感信息过滤
    
    使用方法：
    ```python
    from app.middlewares.logging import RequestLoggingMiddleware
    
    app = FastAPI()
    app.add_middleware(
        RequestLoggingMiddleware,
        exclude_paths=["/health", "/metrics"],
        sensitive_headers={"authorization", "cookie"}
    )
    ```
    """
    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: set[str] | None = None,
        sensitive_headers: set[str] | None = None,
        log_request_body: bool = False
    ) -> None:
        super().__init__(app)
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}
        self.sensitive_headers = sensitive_headers or {"authorization", "cookie"}
        self.log_request_body = log_request_body
    
    def _mask_sensitive_headers(
        self,
        headers: dict[str, str]
    ) -> dict[str, str]:
        """掩码敏感header信息"""
        return {
            k: "***" if k.lower() in self.sensitive_headers else v
            for k, v in headers.items()
        }
    
    async def log_request(
        self,
        request: Request,
        request_id: str
    ) -> None:
        """记录请求信息"""
        # 获取请求头
        headers = dict(request.headers)
        masked_headers = self._mask_sensitive_headers(headers)
        
        # 基本请求信息
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_host": request.client.host if request.client else None,
            "headers": masked_headers
        }
        
        # 可选择是否记录请求体
        if self.log_request_body:
            try:
                body = await request.json()
                log_data["body"] = body
            except:
                pass
        
        logger.info(
            f"Request received: {request.method} {request.url.path}",
            extra=log_data
        )
    
    async def log_response(
        self,
        response: Response,
        request_id: str,
        duration: float
    ) -> None:
        """记录响应信息"""
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": f"{duration:.3f}s",
                "response_headers": dict(response.headers)
            }
        )
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 检查是否需要跳过日志记录
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 获取请求ID
        request_id = getattr(request.state, "request_id", None)
        if not request_id:
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 记录请求信息
        await self.log_request(request, request_id)
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 计算请求处理时间
            duration = time.time() - start_time
            
            # 记录响应信息
            await self.log_response(response, request_id, duration)
            
            # 添加处理时间到响应头
            response.headers["X-Process-Time"] = f"{duration:.3f}s"
            
            return response
            
        except Exception as e:
            # 记录错误信息
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "duration": f"{duration:.3f}s"
                },
                exc_info=True if settings.DEBUG else False
            )
            raise

class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """
    性能日志中间件
    
    功能：
    1. 记录请求处理时间
    2. 记录慢请求
    3. 记录资源使用情况
    
    使用方法：
    ```python
    from app.middlewares.logging import PerformanceLoggingMiddleware
    
    app = FastAPI()
    app.add_middleware(
        PerformanceLoggingMiddleware,
        slow_request_threshold=1.0  # 1秒
    )
    ```
    """
    def __init__(
        self,
        app: ASGIApp,
        slow_request_threshold: float = 1.0,  # 1秒
        exclude_paths: set[str] | None = None
    ) -> None:
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 检查是否需要跳过
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # 记录慢请求
        if duration > self.slow_request_threshold:
            logger.warning(
                "Slow request detected",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration": f"{duration:.3f}s",
                    "threshold": f"{self.slow_request_threshold:.3f}s"
                }
            )
        
        # 如果开启了DEBUG模式，记录所有请求的性能信息
        if settings.DEBUG:
            logger.debug(
                "Request performance metrics",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration": f"{duration:.3f}s",
                    "status_code": response.status_code
                }
            )
        
        return response

# 使用示例
"""
from fastapi import FastAPI
from app.middlewares.logging import (
    RequestLoggingMiddleware,
    PerformanceLoggingMiddleware
)

app = FastAPI()

# 添加中间件（注意顺序）
app.add_middleware(
    RequestLoggingMiddleware,
    exclude_paths={"/health", "/metrics"},
    sensitive_headers={"authorization", "cookie"},
    log_request_body=settings.DEBUG
)

app.add_middleware(
    PerformanceLoggingMiddleware,
    slow_request_threshold=1.0,
    exclude_paths={"/health", "/metrics"}
)
"""