# core/events.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.api.router import router

async def startup_handler() -> None:
    """
    应用启动时的处理函数
    """
    # 数据库连接初始化等操作
    pass

async def shutdown_handler() -> None:
    """
    应用关闭时的处理函数
    """
    # 清理资源等操作
    pass

def configure_middleware(app: FastAPI) -> None:
    """
    配置中间件
    """
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # 生产环境需要配置具体的允许域名
    )

def configure_routers(app: FastAPI) -> None:
    """
    配置路由
    """
    # 注册API路由
    app.include_router(router, prefix=settings.API_V1_STR)

def configure_exception_handlers(app: FastAPI) -> None:
    """
    配置全局异常处理
    """
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # 全局异常处理
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal Server Error",
                "detail": str(exc) if settings.DEBUG else "An error occurred"
            }
        )
