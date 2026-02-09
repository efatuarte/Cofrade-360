#!/bin/bash

# Quick start script for Cofrade-360

echo "🙏 Cofrade 360 - Quick Start"
echo "=============================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Start services
echo "🚀 Starting services (PostGIS, Redis, MinIO, API)..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "🌐 Access points:"
echo "   - API:          http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/docs"
echo "   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "📝 To view logs:"
echo "   docker compose logs -f api"
echo ""
echo "🛑 To stop services:"
echo "   docker compose down"
echo ""
