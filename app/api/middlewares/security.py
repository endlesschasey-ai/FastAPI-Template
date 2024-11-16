# middlewares/security.py
import time
import re
from typing import Callable, Optional
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from redis import Redis
from app.utils.logger import get_logger
from app.core.config import settings

logger = get_logger()

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    请求限流中间件
    
    功能：
    1. 基于IP的请求限流
    2. 支持不同路径不同限流规则
    3. 支持Redis分布式限流
    4. 灵活的限流策略配置
    
    使用方法：
    ```python
    from app.middlewares.security import RateLimitingMiddleware
    
    app = FastAPI()
    app.add_middleware(
        RateLimitingMiddleware,
        rate_limit=100,  # 默认限制每分钟100次请求
        rate_limit_by_path={
            "/api/v1/auth/login": 5  # 登录接口每分钟限制5次
        }
    )
    ```
    """
    def __init__(
        self,
        app: ASGIApp,
        redis_client: Optional[Redis] = None,
        rate_limit: int = 100,  # 默认每分钟请求数
        rate_limit_by_path: dict[str, int] | None = None,
        window_size: int = 60,  # 时间窗口(秒)
        exclude_paths: set[str] | None = None
    ) -> None:
        super().__init__(app)
        self.redis = redis_client
        self.rate_limit = rate_limit
        self.rate_limit_by_path = rate_limit_by_path or {}
        self.window_size = window_size
        self.exclude_paths = exclude_paths or {"/health", "/metrics"}
    
    def _get_rate_limit(self, path: str) -> int:
        """获取特定路径的限流值"""
        return self.rate_limit_by_path.get(path, self.rate_limit)
    
    async def _check_rate_limit(
        self,
        key: str,
        limit: int
    ) -> tuple[bool, int]:
        """检查是否超过限流"""
        current_time = int(time.time())
        window_start = current_time - self.window_size
        
        if self.redis:
            # 使用Redis进行分布式限流
            pipeline = self.redis.pipeline()
            pipeline.zremrangebyscore(key, 0, window_start)
            pipeline.zadd(key, {str(current_time): current_time})
            pipeline.zcard(key)
            pipeline.expire(key, self.window_size)
            _, _, count, _ = pipeline.execute()
        else:
            # 内存限流(不推荐用于生产环境)
            if not hasattr(self, '_requests'):
                self._requests = {}
            if key not in self._requests:
                self._requests[key] = []
                
            self._requests[key] = [
                ts for ts in self._requests[key] 
                if ts > window_start
            ]
            self._requests[key].append(current_time)
            count = len(self._requests[key])
            
        return count <= limit, count
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 检查是否需要跳过限流
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 获取当前路径的限流值
        rate_limit = self._get_rate_limit(request.url.path)
        
        # 限流键(可以基于IP、路径等组合)
        rate_limit_key = f"rate_limit:{client_ip}:{request.url.path}"
        
        # 检查限流
        is_allowed, current_count = await self._check_rate_limit(
            rate_limit_key,
            rate_limit
        )
        
        if not is_allowed:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "count": current_count,
                    "limit": rate_limit
                }
            )
            return Response(
                content="Too Many Requests",
                status_code=429,
                headers={"Retry-After": str(self.window_size)}
            )
        
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    安全响应头中间件
    
    功能：
    1. 添加常用安全响应头
    2. XSS防护
    3. CSRF保护
    4. 点击劫持防护
    
    使用方法：
    ```python
    from app.middlewares.security import SecurityHeadersMiddleware
    
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    ```
    """
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        response = await call_next(request)
        
        # 添加安全响应头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        
        return response

class SQLInjectionMiddleware(BaseHTTPMiddleware):
    """
    SQL注入防护中间件
    
    功能：
    1. 检测常见SQL注入模式
    2. 记录可疑请求
    3. 阻止可疑请求
    
    使用方法：
    ```python
    from app.middlewares.security import SQLInjectionMiddleware
    
    app = FastAPI()
    app.add_middleware(
        SQLInjectionMiddleware,
        block_suspicious=True  # 阻止可疑请求
    )
    ```
    """
    def __init__(
        self,
        app: ASGIApp,
        block_suspicious: bool = True
    ) -> None:
        super().__init__(app)
        self.block_suspicious = block_suspicious
        
        # SQL注入检测模式
        self.sql_patterns = [
            r"(?i)(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER).*?;",
            r"(?i)(\b(AND|OR)\b\s+\w+\s*=\s*\w+)",
            r"(?i)(--|\#|\/\*|\*\/)",
            r"(?i)(\bEXEC\b|\bLIKE\b)",
            r"(?i)(\bSYSTEM\b|\bUSER\b|\bDATABASE\b)",
            r"'.*?';\s*--",
            r"\b(CONCAT|CHAR|ASCII)\b.*?\(",
        ]
        
        # 编译正则表达式
        self.patterns = [re.compile(pattern) for pattern in self.sql_patterns]
    
    def _check_sql_injection(self, text: str) -> bool:
        """检查是否包含SQL注入模式"""
        return any(pattern.search(text) for pattern in self.patterns)
    
    async def _get_request_data(self, request: Request) -> dict:
        """获取请求数据"""
        data = {
            "query_params": str(request.query_params),
            "path_params": str(request.path_params),
        }
        
        # 检查请求体
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
                data["body"] = str(body)
            except:
                pass
                
        return data
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # 获取请求数据
        request_data = await self._get_request_data(request)
        
        # 检查所有数据是否包含SQL注入
        for key, value in request_data.items():
            if self._check_sql_injection(value):
                logger.warning(
                    "Potential SQL injection detected",
                    extra={
                        "client_ip": request.client.host,
                        "path": request.url.path,
                        "method": request.method,
                        "suspicious_data": {key: value}
                    }
                )
                
                if self.block_suspicious:
                    return Response(
                        content="Invalid request",
                        status_code=400
                    )
        
        return await call_next(request)

# 使用示例
"""
from fastapi import FastAPI
from app.middlewares.security import (
    RateLimitingMiddleware,
    SecurityHeadersMiddleware,
    SQLInjectionMiddleware
)

app = FastAPI()

# 添加中间件（注意顺序）
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    RateLimitingMiddleware,
    rate_limit=100,
    rate_limit_by_path={
        "/api/v1/auth/login": 5
    },
    redis_client=redis_client  # 可选，用于分布式限流
)

app.add_middleware(
    SQLInjectionMiddleware,
    block_suspicious=True
)
"""