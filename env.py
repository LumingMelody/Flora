"""
Flora 全局环境变量配置
"""
import os

# Redis 配置
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DATABASE = int(os.getenv('REDIS_DATABASE', '0'))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None) or None

# RabbitMQ 配置
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

# MySQL 配置
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
MYSQL_CHARSET = os.getenv('MYSQL_CHARSET', 'utf8mb4')
MYSQL_MAX_CONNECTIONS = int(os.getenv('MYSQL_MAX_CONNECTIONS', '5'))

# PostgreSQL 配置
POSTGRESQL_HOST = os.getenv('POSTGRESQL_HOST', 'localhost')
POSTGRESQL_PORT = int(os.getenv('POSTGRESQL_PORT', '5432'))
POSTGRESQL_USER = os.getenv('POSTGRESQL_USER', 'user')
POSTGRESQL_PASSWORD = os.getenv('POSTGRESQL_PASSWORD', 'pass')

# Neo4j 配置
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

# LLM 配置
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')

# Dify 配置
DIFY_API_KEY = os.getenv('DIFY_API_KEY', '')
DIFY_BASE_URL = os.getenv('DIFY_BASE_URL', '')

# Memory 配置
MEM0_API_KEY = os.getenv('MEM0_API_KEY', '')
MEM0_BASE_URL = os.getenv('MEM0_BASE_URL', '')

# 设置 OpenAI 兼容环境变量（Mem0 依赖）
if DASHSCOPE_API_KEY:
    os.environ["OPENAI_API_KEY"] = DASHSCOPE_API_KEY
    os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# Mem0 配置
MEM0_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "user_memories",
            "path": "./chroma_db",
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "qwen-plus",
            "temperature": 0.1,
            "max_tokens": 4096
        }
    },
    "memory": {
        "type": "graph",
        "enable_reasoning": True,
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-v2",
        }
    },
}

# 数据库类型
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')

# 其他配置
FLORA_DATA_DIR = os.getenv('FLORA_DATA_DIR', './data')

# Text-to-SQL 配置
MIN_RESULT_ROWS = int(os.getenv('MIN_RESULT_ROWS', '1'))  # 至少返回 1 行才学习
MAX_SQL_LENGTH = int(os.getenv('MAX_SQL_LENGTH', '1000'))  # 防止超长 SQL
ALLOWED_TABLES = None  # 可设为白名单，如 ["sales", "users"]
VANNA_TYPE = os.getenv('VANNA_TYPE', 'qwen_chroma')  # Vanna 实现类型

# Memory 存储配置
env = os.getenv("ENV", "dev")
if env == "prod":
    MEMORY_CONFIG = {
        "vault": {
            "db_path": "/secure/vault.db",
            "encryption_key_b64": os.getenv("VAULT_KEY")
        },
        "resource": {
            "db_path": "/data/resources.db",
            "use_minio": True,
            "minio_endpoint": os.getenv("MINIO_ENDPOINT", "minio:9000"),
            "minio_access_key": os.getenv("MINIO_ACCESS_KEY"),
            "minio_secret_key": os.getenv("MINIO_SECRET_KEY"),
            "local_dir": None
        },
        "procedural": {
            "dir": "/app/procedures"
        }
    }
else:
    MEMORY_CONFIG = {
        "vault": {"db_path": "vault_dev.db", "encryption_key_b64": None},
        "resource": {"db_path": "resources_dev.db", "use_minio": False, "local_dir": "files_dev"},
        "procedural": {"dir": "procedures_dev"}
    }
