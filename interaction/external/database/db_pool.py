# interaction/external/database/db_pool.py
"""
数据库连接池抽象层，支持 SQLite 和 MySQL 切换
通过环境变量 DB_TYPE 控制使用哪种数据库
"""

import os
import logging
from typing import Union, Any

logger = logging.getLogger(__name__)

# 数据库类型：sqlite 或 mysql
DB_TYPE = os.getenv('DB_TYPE', 'sqlite').lower()


class DatabasePool:
    """
    数据库连接池抽象类
    根据 DB_TYPE 环境变量自动选择 SQLite 或 MySQL
    """

    def __init__(self, db_name: str = "default", **kwargs):
        """
        初始化数据库连接池

        Args:
            db_name: 数据库名称（SQLite 为文件名，MySQL 为数据库名）
            **kwargs: 其他数据库特定参数
        """
        self.db_type = DB_TYPE
        self.db_name = db_name
        self._pool = None

        if self.db_type == 'mysql':
            from .mysql_pool import MySQLConnectionPool
            # MySQL 使用数据库名
            database = kwargs.pop('database', None) or f"flora_{db_name}"
            self._pool = MySQLConnectionPool(database=database, **kwargs)
            self._is_mysql = True
        else:
            from .sqlite_pool import SQLiteConnectionPool
            # SQLite 使用文件路径
            db_path = kwargs.pop('db_path', None) or f"{db_name}.db"
            self._pool = SQLiteConnectionPool(db_path=db_path, **kwargs)
            self._is_mysql = False

        logger.info(f"DatabasePool initialized: type={self.db_type}, name={db_name}")

    @property
    def is_mysql(self) -> bool:
        return self._is_mysql

    @property
    def placeholder(self) -> str:
        """返回 SQL 占位符：MySQL 用 %s，SQLite 用 ?"""
        return '%s' if self._is_mysql else '?'

    def get_connection(self) -> Any:
        """获取数据库连接"""
        return self._pool.get_connection()

    def return_connection(self, conn: Any):
        """归还数据库连接"""
        self._pool.return_connection(conn)

    def close_all(self):
        """关闭所有连接"""
        self._pool.close_all()

    def execute(self, sql: str, params: tuple = None) -> Any:
        """
        执行 SQL 语句（自动处理占位符转换）

        Args:
            sql: SQL 语句（使用 ? 作为占位符）
            params: 参数元组

        Returns:
            cursor 对象
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            # 如果是 MySQL，将 ? 转换为 %s
            if self._is_mysql:
                sql = sql.replace('?', '%s')
            cursor.execute(sql, params or ())
            return cursor, conn
        except Exception as e:
            self.return_connection(conn)
            raise e

    def execute_and_commit(self, sql: str, params: tuple = None) -> int:
        """
        执行 SQL 并提交，返回影响的行数

        Args:
            sql: SQL 语句
            params: 参数元组

        Returns:
            影响的行数
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self._is_mysql:
                sql = sql.replace('?', '%s')
            cursor.execute(sql, params or ())
            conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount
        finally:
            self.return_connection(conn)

    def fetch_one(self, sql: str, params: tuple = None) -> Any:
        """执行查询并返回单行结果"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self._is_mysql:
                sql = sql.replace('?', '%s')
            cursor.execute(sql, params or ())
            result = cursor.fetchone()
            cursor.close()
            return result
        finally:
            self.return_connection(conn)

    def fetch_all(self, sql: str, params: tuple = None) -> list:
        """执行查询并返回所有结果"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            if self._is_mysql:
                sql = sql.replace('?', '%s')
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
        finally:
            self.return_connection(conn)

    def __del__(self):
        if self._pool:
            self.close_all()


def get_insert_or_replace_sql(table: str, columns: list, is_mysql: bool) -> str:
    """
    生成 INSERT OR REPLACE 语句（兼容 SQLite 和 MySQL）

    Args:
        table: 表名
        columns: 列名列表
        is_mysql: 是否为 MySQL

    Returns:
        SQL 语句
    """
    placeholders = ', '.join(['%s' if is_mysql else '?' for _ in columns])
    columns_str = ', '.join(columns)

    if is_mysql:
        # MySQL 使用 REPLACE INTO
        return f"REPLACE INTO {table} ({columns_str}) VALUES ({placeholders})"
    else:
        # SQLite 使用 INSERT OR REPLACE
        return f"INSERT OR REPLACE INTO {table} ({columns_str}) VALUES ({placeholders})"


def get_create_index_sql(index_name: str, table: str, columns: list, is_mysql: bool) -> str:
    """
    生成创建索引的 SQL（兼容 SQLite 和 MySQL）
    """
    columns_str = ', '.join(columns)
    # 两者语法相同
    return f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({columns_str})"
