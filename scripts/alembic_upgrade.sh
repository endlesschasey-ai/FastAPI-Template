#!/bin/bash

# 检查是否提供了迁移注释
if [ -z "$1" ]
then
    echo "请提供迁移注释"
    echo "使用方法: ./scripts/alembic_upgrade.sh '迁移说明'"
    exit 1
fi

# 生成迁移文件
alembic revision --autogenerate -m "$1"

# 执行迁移
alembic upgrade head

echo "✅ 数据库迁移完成" 