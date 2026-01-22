# config.py

import os

# Neo4j 配置（从环境变量读取）
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://121.36.203.36:10008")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

# Redis 配置（从环境变量读取）
REDIS_HOST = os.getenv("REDIS_HOST", "121.36.203.36")
REDIS_PORT = int(os.getenv("REDIS_PORT", "10002"))
REDIS_DATABASE = int(os.getenv("REDIS_DATABASE", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "lanba888")



MAX_TASK_DURATION = 300

# DashScope (Qwen)
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# Dify 配置
DIFY_URI = os.getenv("DIFY_BASE_URL", "http://121.36.203.36:81/v1")


CONNECTOR_RECORD_DB_URL = "sqlite:///dify_runs.db"



# MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "121.36.203.36")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "8889"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "ZKLB.EQiAI@2025!")
MYSQL_MAX_CONNECTIONS = int(os.getenv("MYSQL_MAX_CONNECTIONS", "20"))
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET", "utf8mb4")

# PostgreSQL 配置
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "localhost")
POSTGRESQL_PORT = int(os.getenv("POSTGRESQL_PORT", "5432"))
POSTGRESQL_USER = os.getenv("POSTGRESQL_USER", "postgres")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD", "")
POSTGRESQL_MAX_CONNECTIONS = int(os.getenv("POSTGRESQL_MAX_CONNECTIONS", "20"))

# SQL Server 配置
SQLSERVER_HOST = os.getenv("SQLSERVER_HOST", "localhost")
SQLSERVER_PORT = int(os.getenv("SQLSERVER_PORT", "1433"))
SQLSERVER_USER = os.getenv("SQLSERVER_USER", "sa")
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD", "")
SQLSERVER_DRIVER = os.getenv("SQLSERVER_DRIVER", "{ODBC Driver 17 for SQL Server}")
SQLSERVER_MAX_CONNECTIONS = int(os.getenv("SQLSERVER_MAX_CONNECTIONS", "20"))

# Oracle 配置
ORACLE_HOST = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_USER = os.getenv("ORACLE_USER", "system")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "")
ORACLE_SID = os.getenv("ORACLE_SID", "")
ORACLE_MAX_CONNECTIONS = int(os.getenv("ORACLE_MAX_CONNECTIONS", "20"))



# Chroma
CHROMA_PERSIST_DIR = "./chroma_storage"

# 学习策略
MIN_RESULT_ROWS = 1          # 至少返回 1 行才学习
MAX_SQL_LENGTH = 1000        # 防止超长 SQL
ALLOWED_TABLES = None        # 可设为白名单，如 ["sales", "users"]




# DashScope (Qwen) API Key
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")
# 关键：设置 OPENAI_API_KEY 环境变量（Mem0 依赖它）
os.environ["OPENAI_API_KEY"] = DASHSCOPE_API_KEY
# 同时设置 base_url（有些 SDK 也依赖这个）
os.environ["OPENAI_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
# Mem0 配置
MEM0_CONFIG = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "user_memories",
            "path": "./chroma_db",  # 本地存储路径
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
        "type": "graph",  # 可选: "vector" 或 "graph"
        "enable_reasoning": True,  # 启用推理式记忆提取
    },
     "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-v2",

        }
    },
}


env = os.getenv("ENV", "dev")
MEMORY_CONFIG ={}
# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
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
    MEMORY_CONFIG= {
        "vault": {"db_path": "vault_dev.db", "encryption_key_b64": None},  # 明文模式
        "resource": {"db_path": "resources_dev.db", "use_minio": False, "local_dir": "files_dev"},
        "procedural": {"dir": "procedures_dev"}
    }


# config.py
VECTOR_DIM = 8          # Optuna 采样的隐向量维度（固定）
MAX_CONCURRENT = 3
OPTIMIZATION_ROUNDS = 5
SYSTEM_ROLE = """
你是一个自动化优化系统的智能编排器。
你的任务是：
1. 根据用户目标，动态定义需要优化的维度；
2. 将隐向量解码为可执行指令；
3. 从原始输出中提取数值分数。
所有输出必须严格遵循指定 JSON 格式。
"""

# 能力配置
CAPABILITIES_CONFIG = {
    "llm": {
        "qwen": {
            "api_key": DASHSCOPE_API_KEY,
            "model_name": "qwen-max",
            "vl_model_name": "qwen-vl-max"
        }
    },
    "memory": {
        "core_memory": {
            "user_id": "default_user",
            "cache_ttl": 3600,
            "cache_maxsize": 500,
            "mem0_config": MEM0_CONFIG,
            "memory_config": MEMORY_CONFIG
        }
    },
    "text_to_sql": {
        "vanna": "qwen_chroma"
    }
}


VANNA_TYPE="qwen_chroma"
# 全局配置
GLOBAL_CONFIG = {
    "log_level": LOG_LEVEL
}



RABBITMQ_HOST='192.168.10.33',
RABBITMQ_PORT=5672,
RABBITMQ_USERNAME='admin',
RABBITMQ_PASSWORD='411510',
RABBITMQ_VIRTUAL_HOST='/',
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://admin:Lanba%40123@121.36.203.36:10005/prod")
