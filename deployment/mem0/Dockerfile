FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（psycopg 需要编译，需要 libpq-dev 和 python3-dev）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY projects/mem0/server/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务器代码
COPY projects/mem0/server/ .

# 创建历史数据库目录
RUN mkdir -p /app/history

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

