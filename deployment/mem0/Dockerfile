FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（patch 和 wget 用于应用补丁和健康检查）
RUN apt-get update && apt-get install -y \
    patch \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY projects/mem0/server/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务器代码
COPY projects/mem0/server/ .

# 应用补丁（在构建时应用，不修改源文件）
# 使用合并补丁文件，包含所有修改（CORS、中文语言支持、Qdrant、API 前缀）
COPY deployment/mem0/patches/all-in-one.patch /tmp/all-in-one.patch
COPY deployment/mem0/patches/fix-json-prompt.patch /tmp/fix-json-prompt.patch
COPY deployment/mem0/patches/fix-memory-update-error.patch /tmp/fix-memory-update-error.patch
RUN cd /app && \
    patch -p0 < /tmp/all-in-one.patch || (echo "ERROR: All-in-one patch failed!" && exit 1) && \
    (MEM0_PATH=$(python3 -c "import mem0.memory.main; import os; print(os.path.dirname(mem0.memory.main.__file__))") && \
     patch -p1 -d "$MEM0_PATH" < /tmp/fix-json-prompt.patch || echo "Warning: JSON prompt fix patch failed, continuing..." && \
     patch -p1 -d "$MEM0_PATH" < /tmp/fix-memory-update-error.patch || (echo "ERROR: Fix memory update error patch failed!" && exit 1)) && \
    true

# 创建历史数据库目录
RUN mkdir -p /app/history

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

