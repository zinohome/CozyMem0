FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（psycopg 需要编译，需要 libpq-dev 和 python3-dev，patch 用于应用补丁）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    python3-dev \
    patch \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY projects/mem0/server/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务器代码
COPY projects/mem0/server/ .

# 应用补丁（在构建时应用，不修改源文件）
COPY deployment/mem0/patches/cors.patch /tmp/cors.patch
COPY deployment/mem0/patches/chinese-language-support.patch /tmp/chinese-language-support.patch
RUN cd /app && \
    patch -p0 < /tmp/cors.patch || (echo "Warning: CORS patch failed, continuing..." && true) && \
    patch -p0 < /tmp/chinese-language-support.patch || (echo "Warning: Chinese language support patch failed, continuing..." && true)

# 创建历史数据库目录
RUN mkdir -p /app/history

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

