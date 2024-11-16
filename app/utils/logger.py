# utils/logger.py
import logging
import sys
from typing import Any
from pydantic import BaseModel
from loguru import logger, Logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    """
    拦截标准库日志并重定向到loguru
    """
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

class LogConfig(BaseModel):
    """
    日志配置
    """
    LOGGER_NAME: str = "fastapi_template"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_LEVEL: str = "DEBUG" if settings.DEBUG else "INFO"
    
    # 日志处理器配置
    handlers: list[dict[str, Any]] = [
        {"sink": sys.stdout, "format": LOG_FORMAT},
        {"sink": "logs/app.log", "rotation": "20 MB", "format": LOG_FORMAT}
    ]

def setup_logging() -> None:
    """
    配置日志
    """
    # 移除所有default handlers
    logger.configure(handlers=[])
    
    # 加载配置
    log_config = LogConfig()
    
    # 配置loguru
    logger.configure(**log_config.model_dump())
    
    # 拦截标准库日志
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # 设置第三方库的日志级别
    for log_name in ["uvicorn", "uvicorn.error", "fastapi"]:
        logging_logger = logging.getLogger(log_name)
        logging_logger.handlers = [InterceptHandler()]

def get_logger() -> Logger:
    """
    获取logger实例
    """
    return logger