#!/bin/bash
set -e

# Ensure data directory exists and is writable
if [ ! -d "/data" ]; then
    echo "📂 Creating /data directory..."
    mkdir -p /data
fi

# Seed database with existing API keys (if not already seeded)
echo "🌱 Seeding database..."
python seed_db.py || echo "⚠️  Seed script failed or already seeded"

# Start Nginx in background
echo "🚀 Starting Nginx..."
service nginx start

# Start Backend in foreground
echo "🐍 Starting FastAPI Backend..."
# We bind to localhost because Nginx will proxy to us locally
exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
