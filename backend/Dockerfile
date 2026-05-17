# Echomind Commerce - Backend (FastAPI + uvicorn)
FROM python:3.14-slim

# System deps for common Python wheels (audio, lxml, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY . .

EXPOSE 8000

# Default command - can be overridden by docker-compose for dev (--reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
