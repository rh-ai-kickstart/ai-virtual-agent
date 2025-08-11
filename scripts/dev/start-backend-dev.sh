#!/bin/bash

# AI Virtual Agent - Backend Development Startup Script
# This script runs database migrations before starting the development server

set -e

echo "🚀 Starting backend with auto-migrations..."

# Change to backend directory for alembic
cd /app/backend

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! nc -z db 5432; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running migrations..."
alembic upgrade head

echo "✅ Migrations completed!"

# Start the development server
echo "🌟 Starting development server..."
cd /app
exec uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000