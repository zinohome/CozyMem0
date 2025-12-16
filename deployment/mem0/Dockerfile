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
COPY deployment/mem0/patches/cors.patch /tmp/cors.patch
COPY deployment/mem0/patches/chinese-language-support.patch /tmp/chinese-language-support.patch
COPY deployment/mem0/patches/fix-json-prompt.patch /tmp/fix-json-prompt.patch
COPY deployment/mem0/patches/switch-to-qdrant.patch /tmp/switch-to-qdrant.patch
RUN cd /app && \
    patch -p0 < /tmp/cors.patch || (echo "Warning: CORS patch failed, continuing..." && true) && \
    patch -p0 < /tmp/chinese-language-support.patch || (echo "Warning: Chinese language support patch failed, continuing..." && true) && \
    patch -p0 < /tmp/switch-to-qdrant.patch || (echo "Warning: Switch to Qdrant patch failed, continuing..." && true) && \
    (MEM0_PATH=$(python3 -c "import mem0.memory.main; import os; print(os.path.dirname(mem0.memory.main.__file__))") && \
     patch -p1 -d "$MEM0_PATH" < /tmp/fix-json-prompt.patch || echo "Warning: JSON prompt fix patch failed, continuing...") && \
    true

# 创建历史数据库目录
RUN mkdir -p /app/history

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

