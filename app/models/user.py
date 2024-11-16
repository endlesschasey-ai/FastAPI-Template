# models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class User(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(
        String(254), 
        unique=True, 
        index=True,
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"