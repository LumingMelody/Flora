from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from datetime import datetime, timezone
from typing import AsyncGenerator
import os

# 导入配置
from config.settings import settings

# 判断数据库类型
db_type = os.getenv('DB_TYPE', 'sqlite').lower()
is_mysql = db_type == 'mysql' or 'mysql' in settings.database_url

# 根据数据库类型选择连接池
if is_mysql:
    # MySQL 使用连接池
    engine = create_async_engine(
        settings.database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # 自动检测断开的连接
        echo=False,
    )
else:
    # SQLite 使用 NullPool
    engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=False,
    )

# 创建异步会话工厂
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# 获取数据库方言
dialect = engine.dialect.name

# 数据库会话依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

# 自动创建表的函数
async def create_tables():
    """创建所有数据库表"""
    from .models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
