"""Environment settings loaded from .env (project root)."""
from __future__ import annotations

import os
from typing import Any, Dict, List

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _load_dotenv(dotenv_path: str) -> None:
    if not os.path.exists(dotenv_path):
        return
    try:
        with open(dotenv_path, "r", encoding="utf-8") as file:
            for line in file:
                raw = line.strip()
                if not raw or raw.startswith("#"):
                    continue
                if raw.startswith("export "):
                    raw = raw[len("export ") :].strip()
                if "=" not in raw:
                    continue
                key, value = raw.split("=", 1)
                key = key.strip()
                value = value.strip()
                if (
                    (value.startswith('"') and value.endswith('"'))
                    or (value.startswith("'") and value.endswith("'"))
                ):
                    value = value[1:-1]
                os.environ.setdefault(key, value)
    except Exception:
        # Ignore .env parsing errors to avoid blocking startup
        return


_load_dotenv(os.path.join(BASE_DIR, ".env"))


def _split_csv(value: str) -> List[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


DATA_DIR = os.getenv("FLORA_DATA_DIR", os.path.join(BASE_DIR, "data"))

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "")
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")
DIFY_RESPONSE_MODE = os.getenv("DIFY_RESPONSE_MODE", "blocking")
VANNA_TYPE = os.getenv("VANNA_TYPE", "qwen_chroma")

MIN_RESULT_ROWS = int(os.getenv("MIN_RESULT_ROWS", "3"))
MAX_SQL_LENGTH = int(os.getenv("MAX_SQL_LENGTH", "2000"))
ALLOWED_TABLES = _split_csv(os.getenv("ALLOWED_TABLES", ""))

NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USER = os.getenv("NEO4J_USER", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")
MYSQL_MAX_CONNECTIONS = int(os.getenv("MYSQL_MAX_CONNECTIONS", "5"))

POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "localhost")
POSTGRESQL_PORT = int(os.getenv("POSTGRESQL_PORT", "5432"))
POSTGRESQL_USER = os.getenv("POSTGRESQL_USER", "user")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD", "pass")

SQLSERVER_HOST = os.getenv("SQLSERVER_HOST", "localhost")
SQLSERVER_PORT = int(os.getenv("SQLSERVER_PORT", "1433"))
SQLSERVER_USER = os.getenv("SQLSERVER_USER", "")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD", "")
SQLSERVER_DRIVER = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")

ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_USER = os.getenv("ORACLE_USER", "")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_SID = os.getenv("ORACLE_SID", "")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DATABASE = int(os.getenv("REDIS_DATABASE", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

# RabbitMQ 配置
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

# ERP API 配置
ERP_API_BASE_URL = os.getenv("ERP_API_BASE_URL", "")
ERP_API_TOKEN = os.getenv("ERP_API_TOKEN", "")

MEM0_CONFIG: Dict[str, Any] = {
    "api_key": os.getenv("MEM0_API_KEY", ""),
    "base_url": os.getenv("MEM0_BASE_URL", ""),
}

MEMORY_CONFIG: Dict[str, Any] = {
    "vault": {
        "db_path": os.path.join(DATA_DIR, "vault.db"),
        "encryption_key_b64": os.getenv("VAULT_ENCRYPTION_KEY_B64", ""),
    },
    "procedural": {
        "dir": os.path.join(DATA_DIR, "procedural"),
    },
    "resource": {
        "db_path": os.path.join(DATA_DIR, "resource.db"),
        "local_dir": os.path.join(DATA_DIR, "resources"),
        "use_minio": os.getenv("MEMORY_USE_MINIO", "false").lower() == "true",
        "minio_endpoint": os.getenv("MINIO_ENDPOINT", ""),
        "minio_access_key": os.getenv("MINIO_ACCESS_KEY", ""),
        "minio_secret_key": os.getenv("MINIO_SECRET_KEY", ""),
    },
}
