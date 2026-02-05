# This Dockerfile is a fallback for systems that expect a Dockerfile at the root.
# It builds the backend service by default.
# For the full stack (Frontend + Backend + Database), use docker-compose.yml.

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create uploads directory
RUN mkdir -p /tmp/uploads

EXPOSE 80

# Production command - Running on Port 80 for compatibility
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
