#!/bin/bash

# AI Virtual Agent - Development Environment Startup Script
# This script replaces the manual 4-terminal setup with a single command

set -e

# Change to project root directory
cd "$(dirname "$0")/../../.."

echo "🚀 Starting AI Virtual Agent Development Environment..."

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Error: podman is not installed or not in PATH"
    echo "Please install podman to continue"
    exit 1
fi

# Check if podman compose is available
if ! podman compose --help &> /dev/null; then
    echo "❌ Error: podman compose is not available"
    echo "Please ensure you have podman-compose installed or use 'podman-compose' instead"
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📄 Creating .env from template..."
    cp .env.example .env
    echo "✅ Created .env - you can customize it if needed"
fi

# Ensure ollama is running (required for LlamaStack)
echo "🦙 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama is not running. Please start Ollama first:"
    echo "   ollama serve"
    echo ""
    echo "   Then load the required model:"
    echo "   echo '/bye' | ollama run llama3.2:3b-instruct-fp16 --keepalive 60m"
    echo ""
    read -p "Press Enter once Ollama is running and the model is loaded..."
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
podman compose -f deploy/local/compose.dev.yaml down --remove-orphans

# Start all services
echo "🏗️  Building and starting all services..."
podman compose -f deploy/local/compose.dev.yaml up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service status
echo "📊 Service Status:"
podman compose -f deploy/local/compose.dev.yaml ps

# Show helpful information
echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:    http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   Database:    postgresql://admin:password@localhost:5432/ai_virtual_agent"
echo "   LlamaStack:  http://localhost:8321"
echo ""
echo "📚 Useful commands:"
echo "   View logs:      podman compose -f compose.dev.yaml logs -f"
echo "   Stop services:  ./scripts/dev/stop-dev.sh"
echo "   Restart:        podman compose -f compose.dev.yaml restart [service]"
echo ""
echo "🔧 Development features:"
echo "   ✅ Hot reload enabled for backend and frontend"
echo "   ✅ Database persisted in volume"
echo "   ✅ Auto-migrations run on startup"
echo ""