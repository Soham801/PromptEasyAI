FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROMPTEASY_ENV=production

WORKDIR /app

# Install system dependencies for HTTPS
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    openssl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

# Create directories for storage and certificates
RUN mkdir -p /var/lib/prompteasy /etc/ssl/certs /etc/ssl/private && \
    chown -R nobody:nogroup /var/lib/prompteasy

# Set default storage path
ENV PROMPTEASY_STORAGE_PATH=/var/lib/prompteasy/prompteasy.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

EXPOSE 8000

# Run as non-root user for security
USER nobody

CMD ["uvicorn", "prompteasy.service:app", "--host", "0.0.0.0", "--port", "8000"]