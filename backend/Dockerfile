# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Matchly AI – Backend Dockerfile
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# System dependencies for PyMuPDF and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
        libmupdf-dev \
        libglib2.0-0 \
        libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/api/health')"

# Switch to non-root user
USER appuser

# Expose default port
EXPOSE 8000

# Start with Uvicorn; PORT env var is respected for platform hosting (Render, etc.)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
