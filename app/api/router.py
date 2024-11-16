# api/router.py
from fastapi import APIRouter
from app.api.endpoints import user, auth

# 创建主路由
router = APIRouter()

# 注册各模块路由
router.include_router(auth.router, prefix="/auth", tags=["认证"])
router.include_router(user.router, prefix="/users", tags=["用户"])