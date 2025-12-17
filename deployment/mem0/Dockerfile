FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖（wget 用于健康检查）
RUN apt-get update && apt-get install -y \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY projects/mem0/server/requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制服务器代码
COPY projects/mem0/server/ .

# 应用补丁（使用 Python 脚本，比 diff 补丁更可靠）
# 1. apply_server_fixes.py: 修改 server/main.py（CORS、Qdrant、API 前缀）
# 2. apply_memory_fixes.py: 修复 mem0/memory/main.py 中的 bugs
COPY deployment/mem0/patches/apply_server_fixes.py /tmp/apply_server_fixes.py
COPY deployment/mem0/patches/apply_memory_fixes.py /tmp/apply_memory_fixes.py
RUN echo "Applying server fixes..." && \
    python3 /tmp/apply_server_fixes.py /app/main.py && \
    echo "Applying memory fixes..." && \
    MEM0_PATH=$(python3 -c "import mem0.memory.main; import os; print(os.path.dirname(mem0.memory.main.__file__))") && \
    python3 /tmp/apply_memory_fixes.py "$MEM0_PATH/main.py" && \
    echo "All fixes applied successfully!"

# 创建历史数据库目录
RUN mkdir -p /app/history

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

