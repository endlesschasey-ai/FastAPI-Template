# middlewares/response.py
import time
import uuid
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.utils.logger import get_logger

logger = get_logger()

class ResponseMiddleware(BaseHTTPMiddleware):
    """
    响应处理中间件
    
    功能：
    1. 为每个请求添加唯一请求ID
    2. 记录请求处理时间
    3. 统一响应格式
    
    使用方法：
    ```python
    from app.middlewares.response import ResponseMiddleware
    
    app = FastAPI()
    app.add_middleware(ResponseMiddleware)
    ```
    """
    def __init__(
        self, 
        app: ASGIApp,
        request_id_header: str = "X-Request-ID",
        process_time_header: str = "X-Process-Time",
    ) -> None:
        super().__init__(app)
        self.request_id_header = request_id_header
        self.process_time_header = process_time_header
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 处理请求
            response = await call_next(request)
            
            # 添加请求ID到响应头
            response.headers[self.request_id_header] = request_id
            
            # 计算并添加处理时间到响应头
            process_time = time.time() - start_time
            response.headers[self.process_time_header] = str(process_time)
            
            # 记录请求信息
            logger.info(
                f"Request processed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "process_time": process_time,
                    "status_code": response.status_code
                }
            )
            
            return response
            
        except Exception as e:
            # 记录错误
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e)
                }
            )
            raise

class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    请求验证中间件
    
    功能：
    1. 验证请求内容类型
    2. 验证请求大小
    3. 基本的请求清理
    
    使用方法：
    ```python
    from app.middlewares.response import RequestValidationMiddleware
    
    app = FastAPI()
    app.add_middleware(
        RequestValidationMiddleware,
        max_content_length=1024*1024  # 1MB
    )
    ```
    """
    def __init__(
        self,
        app: ASGIApp,
        max_content_length: int = 1024 * 1024,  # 1MB
        allowed_content_types: set[str] | None = None
    ) -> None:
        super().__init__(app)
        self.max_content_length = max_content_length
        self.allowed_content_types = allowed_content_types or {
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data"
        }
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 验证Content-Type
        content_type = request.headers.get("content-type", "").split(";")[0]
        if content_type and content_type not in self.allowed_content_types:
            return Response(
                content="Unsupported Media Type",
                status_code=415
            )
        
        # 验证Content-Length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_content_length:
            return Response(
                content="Request Entity Too Large",
                status_code=413
            )
        
        return await call_next(request)

# 使用示例
"""
from fastapi import FastAPI
from app.middlewares.response import ResponseMiddleware, RequestValidationMiddleware

app = FastAPI()

# 添加中间件（注意顺序）
app.add_middleware(
    ResponseMiddleware,
    request_id_header="X-Request-ID",
    process_time_header="X-Process-Time"
)

app.add_middleware(
    RequestValidationMiddleware,
    max_content_length=1024*1024,  # 1MB
    allowed_content_types={
        "application/json",
        "multipart/form-data"
    }
)
"""