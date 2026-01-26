import json
import os
import time
from typing import Dict, Any
from urllib.parse import quote_plus
from pydantic import PrivateAttr
from pydantic_settings import BaseSettings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def get_database_url():
    """根据环境变量构建数据库 URL"""
    db_type = os.getenv('DB_TYPE', 'postgresql').lower()

    if db_type == 'mysql':
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = os.getenv('MYSQL_PORT', '3306')
        user = os.getenv('MYSQL_USER', 'root')
        password = quote_plus(os.getenv('MYSQL_PASSWORD', ''))  # URL 编码密码
        database = os.getenv('MYSQL_DATABASE', 'flora_events')
        return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
    elif db_type == 'sqlite':
        return "sqlite+aiosqlite:///./events.db"
    else:
        # 默认 PostgreSQL
        host = os.getenv('POSTGRESQL_HOST', 'localhost')
        port = os.getenv('POSTGRESQL_PORT', '5432')
        user = os.getenv('POSTGRESQL_USER', 'user')
        password = quote_plus(os.getenv('POSTGRESQL_PASSWORD', 'pass'))
        database = os.getenv('POSTGRESQL_DATABASE', 'command_tower')
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"


class SettingsConfigHandler(FileSystemEventHandler):
    """监控配置文件变化的事件处理器"""
    
    def __init__(self, settings_instance):
        self.settings_instance = settings_instance
    
    def on_modified(self, event):
        """当配置文件被修改时触发"""
        if event.src_path == self.settings_instance._full_config_path:
            print(f"配置文件 {event.src_path} 已修改，重新加载配置...")
            self.settings_instance.load_config()


# 默认配置文件路径
DEFAULT_CONFIG_FILE_PATH = "../event_config.json"


class Settings(BaseSettings):
    # 数据库配置
    db_url: str = ""

    # Redis 配置
    redis_url: str = ""
    use_redis: bool = False

    # RabbitMQ 配置
    rabbitmq_url: str = ""

    # 服务配置
    worker_callback_url: str = ""

    # FastAPI 配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 健康检查配置
    health_check_interval: int = 60
    task_timeout_sec: int = 300
    pending_timeout_sec: int = 3600

    # 私有属性 - 使用 PrivateAttr
    _observer: Observer = PrivateAttr(default=None)
    _full_config_path: str = PrivateAttr(default=None)
    _config_data: Dict[str, Any] = PrivateAttr(default=None)

    def __init__(self, **kwargs):
        # 确定配置文件的绝对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_config_path = os.path.join(base_dir, DEFAULT_CONFIG_FILE_PATH)

        # 读取配置文件
        config_data = self._load_config_file(full_config_path)

        # 调用父类初始化
        super().__init__(**config_data)

        # 设置私有属性
        self._full_config_path = full_config_path
        self._config_data = config_data
        self._observer = None

        # 启动配置文件监控
        self._start_watcher()

    @staticmethod
    def _load_config_file(config_path: str) -> Dict[str, Any]:
        """从 JSON 文件加载配置（静态方法，用于初始化前调用）"""
        # 如果配置文件不存在，创建默认配置
        if not os.path.exists(config_path):
            Settings._create_default_config_file(config_path)

        # 读取配置文件
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        # 环境变量优先覆盖配置文件中的 db_url
        env_db_url = os.getenv("DATABASE_URL")
        if env_db_url:
            config_data["db_url"] = env_db_url
        elif os.getenv("DB_TYPE"):
            # 如果设置了 DB_TYPE，使用 get_database_url() 构建
            config_data["db_url"] = get_database_url()

        # 环境变量覆盖其他配置
        if os.getenv("REDIS_URL"):
            config_data["redis_url"] = os.getenv("REDIS_URL")
        if os.getenv("RABBITMQ_URL"):
            config_data["rabbitmq_url"] = os.getenv("RABBITMQ_URL")
        # 支持通过环境变量启用 Redis EventBus
        use_redis_env = os.getenv("USE_REDIS_EVENT_BUS")
        if use_redis_env is not None:
            config_data["use_redis"] = use_redis_env.lower() in ("true", "1", "yes")

        return config_data

    @staticmethod
    def _create_default_config_file(file_path: str):
        """创建默认配置文件"""
        # 使用环境变量构建的 URL 或默认值
        db_url = os.getenv("DATABASE_URL") or get_database_url()

        default_config = {
            "db_url": db_url,
            "redis_url": "redis://localhost:6379/0",
            "use_redis": False,
            "rabbitmq_url": "amqp://guest:guest@localhost:5672/",
            "worker_callback_url": "http://worker-svc:8000",
            "host": "0.0.0.0",
            "port": 8000,
            "health_check_interval": 60,
            "task_timeout_sec": 300,
            "pending_timeout_sec": 3600
        }

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 写入默认配置
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

        print(f"已创建默认配置文件: {file_path}")

    def load_config(self, full_config_path=None):
        """从 JSON 文件重新加载配置"""
        # 使用传入的路径或当前实例的路径
        config_path = full_config_path or self._full_config_path

        # 加载配置
        self._config_data = self._load_config_file(config_path)

        # 更新实例属性
        for key, value in self._config_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _start_watcher(self):
        """启动配置文件监控"""
        # 创建监控器和事件处理器
        event_handler = SettingsConfigHandler(self)
        self._observer = Observer()
        self._observer.schedule(event_handler, path=os.path.dirname(self._full_config_path), recursive=False)
        self._observer.start()
        
        print(f"已启动配置文件监控: {self._full_config_path}")
    
    def __del__(self):
        """停止监控器"""
        try:
            if hasattr(self, '_observer') and self._observer:
                self._observer.stop()
                self._observer.join(timeout=1.0)  # 设置超时，避免阻塞
        except (RuntimeError, AttributeError):
            # 忽略线程未启动或已停止的错误
            pass


# 创建全局设置实例
settings = Settings()
