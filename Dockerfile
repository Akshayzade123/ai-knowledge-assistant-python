# Multi-stage build for production-ready container
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .
COPY src/ ./src/
COPY asgi.py .

# Install dependencies with uv
ENV UV_SYSTEM_PYTHON=1
RUN uv sync --no-dev --frozen

# Production stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder's virtual environment
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY asgi.py .

# Create uploads directory
RUN mkdir -p /app/uploads

# Set Python path and activate virtual environment
ENV PYTHONPATH=/app/src
ENV PATH=/app/.venv/bin:$PATH
ENV VIRTUAL_ENV=/app/.venv

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run application using asgi.py
CMD ["python", "asgi.py"]
