#!/bin/bash

# Start Nginx in background
echo "🚀 Starting Nginx..."
service nginx start

# Start Backend in foreground
echo "🐍 Starting FastAPI Backend..."
# We bind to localhost because Nginx will proxy to us locally
exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
