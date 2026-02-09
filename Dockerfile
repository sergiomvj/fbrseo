# ==========================================
# STAGE 1: Build Frontend
# ==========================================
FROM node:18-alpine as frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
# Build the React app
RUN npm run build

# ==========================================
# STAGE 2: Runtime (Python + Nginx)
# ==========================================
FROM python:3.11-slim

WORKDIR /app

# Install Nginx and system deps
RUN apt-get update && apt-get install -y \
    nginx \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Configure Nginx
# Remove default config
RUN rm /etc/nginx/sites-enabled/default
# Copy our config
COPY nginx/monolith.conf /etc/nginx/conf.d/default.conf
# Ensure nginx runs comfortably
# Ensure nginx runs comfortably
# RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# Setup Backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./app
# Move app content up one level if needed, or adjust imports. 
# Our backend/ structure logic:
# Repo: backend/app -> Container: /app/app
# config.py expects to be in /app/app usually? 
# Check imports: "from app.config import settings" -> means 'app' must be a package in python path.
# If WORKDIR is /app, then 'app' folder is /app/app.
# Python path includes current dir (/app). So "import app.config" works.

# Create uploads directory (for config.settings default)
RUN mkdir -p /tmp/uploads

# Copy Frontend Build from Stage 1
COPY --from=frontend-builder /app/frontend/build /var/www/html

# Copy Startup Script
COPY start.sh .
RUN chmod +x start.sh

# Persist data
VOLUME /data

EXPOSE 80

# Environment variables should be passed by Easypanel
# But defaults in config.py allow startup without them.

CMD ["./start.sh"]
