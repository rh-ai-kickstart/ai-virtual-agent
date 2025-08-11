#!/bin/bash

# AI Virtual Agent - Development Environment Stop Script

set -e

echo "🛑 Stopping AI Virtual Agent Development Environment..."

# Stop all services
podman compose --env-file .env.dev -f compose.dev.yaml down

echo "✅ All services stopped successfully"
echo ""
echo "💡 To remove all data (including database):"
echo "   podman compose --env-file .env.dev -f compose.dev.yaml down --volumes"
echo ""
echo "🔄 To restart:"
echo "   ./scripts/dev/start-dev.sh"