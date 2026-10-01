#!/bin/bash
# ==============================================================================
# Builders LMS - Production Deployment Script
# Targets: Ubuntu 22.04 / 24.04 LTS, Debian 12
# ==============================================================================

set -e

echo "🏗️ Starting Builders LMS Production Deployment..."

# 1. Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install docker first."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || docker compose version >/dev/null 2>&1 || { echo "❌ Docker Compose is not installed."; exit 1; }

# 2. Check environment file
if [ ! -f ".env" ]; then
    if [ -f ".env.production.example" ]; then
        echo "⚠️ .env not found. Copying .env.production.example to .env..."
        cp .env.production.example .env
        echo "❗ Please edit .env with your real domain and credentials before proceeding."
    fi
fi

# 3. Create SSL directories and placeholder if needed
mkdir -p nginx/ssl/live nginx/certbot/www
if [ ! -f "nginx/ssl/live/fullchain.pem" ]; then
    echo "🔐 Generating self-signed SSL placeholder for initial Nginx boot..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/live/privkey.pem \
        -out nginx/ssl/live/fullchain.pem \
        -subj "/C=SA/ST=Riyadh/L=Riyadh/O=BuildersLMS/CN=localhost"
fi

# 4. Start production services
echo "🚀 Launching Docker containers with docker-compose.prod.yml..."
docker compose -f docker-compose.prod.yml up -d

# 5. Check health
echo "⏳ Waiting for services to initialize..."
sleep 15
docker compose -f docker-compose.prod.yml ps

echo "✅ Builders LMS is successfully deployed and running!"
echo "🌐 LMS Portal: https://${SITE_DOMAIN:-localhost}/lms"
echo "⚙️ Frappe Desk: https://${SITE_DOMAIN:-localhost}/app"
