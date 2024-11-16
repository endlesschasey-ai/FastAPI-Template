# app/__init__.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import settings
from app.api.router import router
from app.core.events import (
    startup_handler,
    shutdown_handler,
    configure_middleware,
    configure_routers,
    configure_exception_handlers,
)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    应用生命周期管理
    """
    # 启动事件
    await startup_handler()
    yield
    # 关闭事件
    await shutdown_handler()

def create_app() -> FastAPI:
    """
    工厂函数: 创建FastAPI应用实例
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # 配置中间件
    configure_middleware(app)
    # 配置路由
    configure_routers(app)
    # 配置异常处理
    configure_exception_handlers(app)
    
    return app

# 创建应用实例
app = create_app()