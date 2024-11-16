# utils/security.py
from datetime import datetime, timedelta
from typing import Any, Union
from passlib.context import CryptContext
from jose import jwt

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def create_token(
    subject: Union[str, Any], 
    expires_delta: timedelta,
    secret_key: str,
    algorithm: str = "HS256"
) -> str:
    """创建JWT令牌"""
    if not isinstance(subject, str):
        subject = str(subject)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"exp": expire, "sub": subject}
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt