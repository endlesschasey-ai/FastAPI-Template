# 🚀 FastAPI Backend Template

一个面向现代化开发的FastAPI后端项目模板，采用最新Python特性，集成AI辅助开发工具，支持异步编程范式。助你打造高性能、可维护的Web应用。

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0+-green.svg)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.0+-yellow.svg)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ 特性

### 现代化开发
- 🐍 **Python 3.11+**: 利用最新Python特性提升性能
- ⚡ **全面异步**: 基于asyncio的异步编程范式
- 🎯 **类型安全**: 完整的类型注解支持
- 🔄 **现代ORM**: 基于SQLAlchemy 2.0的异步查询

### AI加持开发
- 🤖 **Cursor集成**: 内置AI编程助手配置
- 📝 **智能提示**: 基于项目上下文的代码建议
- 🔍 **文档链接**: 支持导入最新技术文档
- 💡 **最佳实践**: 内置开发规范和模式指导

### 开发体验
- 📦 **零配置**: 开箱即用的开发环境
- 🔥 **热重载**: 快速的开发反馈
- 🧪 **测试优先**: 完整的测试框架支持
- 📊 **性能监控**: 内置性能分析工具

### 工程化实践
- 🏗️ **模块化**: 清晰的项目结构
- 🔐 **安全性**: 内置安全最佳实践
- 📚 **文档化**: 自动生成的API文档
- 🔄 **CI/CD**: 现代化的持续集成配置

## 🛠️ 技术栈

- 🚀 **FastAPI**: 现代Python Web框架
  - 性能优异
  - 原生异步支持
  - 自动API文档
  
- 📊 **SQLAlchemy 2.0+**: 新一代Python ORM
  - 异步查询支持
  - 类型安全
  - 性能优化
  
- 🔍 **Pydantic 2.0+**: 数据验证
  - 高性能序列化
  - 完整类型支持
  - 原生JSON支持

- 🔐 **安全组件**:
  - JWT认证
  - OAuth2支持
  - CORS配置
  
- 🧪 **测试工具**:
  - Pytest
  - AsyncIO测试支持
  - 性能测试组件

## 🚀 快速开始

### 环境要求
- Python 3.11+
- PostgreSQL 14+
- Redis 7.0+ (可选，用于缓存)

### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/endlesschasey-ai/FastAPI-Template.git
cd fastapi-template
```

2. 创建虚拟环境
```bash
conda create -n fastapi python=3.11
conda activate fastapi
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件配置数据库等信息
```

5. 运行迁移
```bash
# 首次初始化
alembic init alembic  # 创建 alembic 配置

# 后续迁移可以使用便捷脚本
# Linux/Mac
./scripts/alembic_upgrade.sh "迁移说明"    # 例如: ./scripts/alembic_upgrade.sh "add user table"

# Windows
scripts\alembic_upgrade.bat "迁移说明"     # 例如: scripts\alembic_upgrade.bat "add user table"
```

迁移脚本会自动：
- 生成迁移文件
- 执行迁移操作
- 更新数据库到最新状态

> 注意：首次使用时需要给 shell 脚本添加执行权限：
> ```bash
> chmod +x scripts/alembic_upgrade.sh
> ```

访问:
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc
- 性能监控: http://localhost:8000/metrics

## 📁 项目结构

```
app/
├── api/                    # API路由层
│   ├── endpoints/         # API端点
│   │   ├── user.py        # 用户相关
│   │   └── ...            # 其他端点
│   ├── router.py         # 路由注册
│   ├── deps.py            # 依赖注入
│   └── middlewares/       # 中间件
├── core/                  # 核心配置
│   ├── config.py         # 配置管理
│   ├── security.py       # 安全配置
│   └── events.py         # 事件处理
├── db/                    # 数据库
│   ├── session.py        # 会话管理
│   └── base.py           # 基础模型
│   └── repositories/     # 数据访问层
├── models/               # 数据模型
├── schemas/              # Pydantic模型
├── services/            # 业务逻辑层
├── utils/               # 工具函数
│   ├── deps.py          # 依赖工具
│   └── logger.py        # 日志工具
├── tests/               # 测试用例
├── __init__.py          # 包初始化文件
├── scripts/              # 实用脚本
│   ├── alembic_upgrade.sh    # 数据库迁移(Unix)
│   └── alembic_upgrade.bat   # 数据库迁移(Windows)
```

```python
# main.py
from app import app
from core.config import Config

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=Config.SERVER_HOST, 
        port=Config.SERVER_PORT
        reload=Config.DEBUG,
        workers=Config.WORKERS
    )
```

## 💻 开发指南

### 异步开发

项目默认使用异步模式，示例代码:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    item = await session.get(Item, item_id)
    return item
```

### 类型提示

充分利用Python的类型注解:

```python
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
```

### AI辅助开发

本项目使用 Cursor 作为首选的 AI 辅助开发工具。Cursor 通过项目级的提示词配置和文档导入,为开发提供精准的代码建议和最佳实践指导。

1. Cursor 配置

项目根目录包含 `.cursorrules` 文件,定义了AI助手的行为规范:
```yaml
# AI助手角色定义
role: "FastAPI后端专家"
language: "zh-CN"

# 开发规范
conventions:
  - 使用Python 3.11+新特性
  - 优先采用异步编程模式
  - 遵循函数式编程范式
  - 使用类型注解确保类型安全

# 代码风格
style:
  - 使用描述性的变量命名
  - 保持函数简洁,单一职责
  - 优先使用早期返回处理异常
  - 避免深层嵌套的控制结构

# 性能优化
optimization:
  - 异步I/O操作
  - 合理使用缓存
  - 优化数据库查询
  - 避免阻塞操作
```

2. 导入技术文档

Cursor支持导入外部文档来增强AI的知识库:

```bash
# 在Cursor中导入文档
- FastAPI官方文档
- Python 3.11+更新说明
- SQLAlchemy 2.0文档
- 性能优化指南
```

3. 使用建议

- 充分利用AI上下文感知能力
- 通过对话优化代码实现
- 参考AI提供的佳实践
- 结合文档进行技术决策

## 🚀 性能优化

### 异步性能

- 使用连接池
- 实现缓存策略
- 优化数据库查询
- 使用异步后台任务

### 监控指标

- 请求延迟
- 数据库性能
- 内存使用
- CPU负载

## 🔐 安全实践

- JWT令牌认证
- 请求限流
- SQL注入防护
- XSS防护
- CSRF保护


## 📄 开源协议

本项目采用 MIT 协议开源，查看 [LICENSE](LICENSE) 了解更多信息。