#!/bin/bash

echo "🚀 Starting Deployment..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  .env file not found in backend/. Please create one."
    exit 1
fi

# Load variables (basic check)
export $(grep -v '^#' backend/.env | xargs)

# Pull latest changes (if running in git repo)
# git pull origin main

# Build and Start Containers
echo "Building and starting services..."
docker-compose -f docker-compose.prod.yml up -d --build

echo "✅ Deployment Complete!"
echo "Service should be available at http://localhost (or your domain)"
