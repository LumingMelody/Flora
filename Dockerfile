# Flora 多服务 Python 基础镜像
# 用于 events, interaction, tasks, trigger 四个服务

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 配置华为云镜像源
RUN sed -i 's|deb.debian.org|repo.huaweicloud.com|g' /etc/apt/sources.list.d/debian.sources && \
    sed -i 's|security.debian.org|repo.huaweicloud.com|g' /etc/apt/sources.list.d/debian.sources

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    # MySQL 客户端库
    default-libmysqlclient-dev \
    pkg-config \
    # PostgreSQL 客户端库
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 配置 pip 华为云镜像源
RUN pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple && \
    pip config set global.trusted-host repo.huaweicloud.com

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装额外的异步数据库驱动
RUN pip install --no-cache-dir \
    aiomysql \
    pymysql \
    cryptography

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data

# 默认暴露端口（各服务会覆盖）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# 默认命令（由 docker-compose 覆盖）
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
