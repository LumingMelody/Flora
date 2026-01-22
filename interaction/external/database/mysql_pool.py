# interaction/external/database/mysql_pool.py
"""
MySQL 连接池实现，替代 SQLite 连接池
"""

import os
import logging
from typing import Optional
from queue import Queue
import threading
from urllib.parse import unquote_plus

import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


class MySQLConnectionPool:
    """MySQL 连接池，API 兼容 SQLiteConnectionPool"""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        max_connections: int = 5,
        charset: str = 'utf8mb4'
    ):
        # 从环境变量读取配置，支持覆盖
        self.host = host or os.getenv('MYSQL_HOST', 'localhost')
        self.port = port or int(os.getenv('MYSQL_PORT', '3306'))
        self.user = user or os.getenv('MYSQL_USER', 'root')
        # 密码不需要 URL 解码，因为这里直接使用原始密码
        self.password = password or os.getenv('MYSQL_PASSWORD', '')
        self.database = database or os.getenv('MYSQL_DATABASE', 'flora_interaction')
        self.charset = charset or os.getenv('MYSQL_CHARSET', 'utf8mb4')
        self.max_connections = max_connections

        self.connections = Queue(maxsize=max_connections)
        self.lock = threading.Lock()

        # 确保数据库存在
        self._ensure_database()
        # 初始化连接池
        self._initialize_pool()

    def _ensure_database(self):
        """确保数据库存在，如果不存在则创建"""
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                charset=self.charset
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Database '{self.database}' ensured on {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to ensure database: {e}")
            raise

    def _create_connection(self) -> pymysql.Connection:
        """创建单个数据库连接"""
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            cursorclass=DictCursor,
            autocommit=False
        )

    def _initialize_pool(self):
        """初始化连接池"""
        for _ in range(self.max_connections):
            try:
                conn = self._create_connection()
                self.connections.put(conn)
            except Exception as e:
                logger.error(f"Failed to create connection: {e}")
                raise
        logger.info(f"MySQL connection pool initialized with {self.max_connections} connections")

    def get_connection(self) -> pymysql.Connection:
        """获取一个数据库连接"""
        conn = self.connections.get()
        # 检查连接是否有效，无效则重新创建
        try:
            conn.ping(reconnect=True)
        except Exception:
            logger.warning("Connection lost, creating new connection")
            try:
                conn.close()
            except Exception:
                pass
            conn = self._create_connection()
        return conn

    def return_connection(self, conn: pymysql.Connection):
        """归还连接到连接池"""
        try:
            # 回滚未提交的事务
            conn.rollback()
            self.connections.put(conn)
        except Exception as e:
            logger.warning(f"Failed to return connection, creating new one: {e}")
            try:
                conn.close()
            except Exception:
                pass
            try:
                new_conn = self._create_connection()
                self.connections.put(new_conn)
            except Exception as e2:
                logger.error(f"Failed to create replacement connection: {e2}")

    def close_all(self):
        """关闭所有连接"""
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                conn.close()
            except Exception:
                pass
        logger.info("All MySQL connections closed")

    def __del__(self):
        self.close_all()


# 全局连接池实例（延迟初始化）
_global_pool: Optional[MySQLConnectionPool] = None
_pool_lock = threading.Lock()


def get_mysql_pool() -> MySQLConnectionPool:
    """获取全局 MySQL 连接池实例"""
    global _global_pool
    if _global_pool is None:
        with _pool_lock:
            if _global_pool is None:
                _global_pool = MySQLConnectionPool()
    return _global_pool
