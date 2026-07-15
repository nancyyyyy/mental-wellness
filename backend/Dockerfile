# Build context is the REPO ROOT (not backend/), so the image can also
# include knowledge_base/ and artifacts/ - both needed at runtime by
# scripts/ingest_knowledge_base.py. See docker-compose.yml's `build.context`
# and, for Render, render.yaml's `dockerContext`.
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
COPY knowledge_base/ ./knowledge_base/
COPY artifacts/ ./artifacts/

WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
