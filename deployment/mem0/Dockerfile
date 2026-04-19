FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

COPY projects/mem0/server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy upstream server code, then override main.py with our fixed version.
# Our main.py replaces the brittle apply_server_fixes.py patch approach:
#   - Uses Qdrant as vector store (avoids psycopg/libpq dependency of pgvector)
#   - Adds APIRouter with /api/v1 prefix
#   - Adds CORSMiddleware
#   - Supports OPENAI_BASE_URL for custom LLM endpoints
COPY projects/mem0/server/ .
COPY deployment/mem0/main.py /app/main.py

# Apply mem0 library bug fixes (KeyError guards in mem0/memory/main.py)
COPY deployment/mem0/patches/apply_memory_fixes.py /tmp/apply_memory_fixes.py
RUN MEM0_PATH=$(python3 -c "import mem0.memory.main; import os; print(os.path.dirname(mem0.memory.main.__file__))") && \
    python3 /tmp/apply_memory_fixes.py "$MEM0_PATH/main.py" && \
    echo "Memory fixes applied successfully!"

RUN mkdir -p /app/history

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
