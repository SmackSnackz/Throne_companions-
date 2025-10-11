#!/bin/bash

# Throne Companions Backend Startup Script

echo "Starting Throne Companions Backend..."

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | xargs)
else
    echo "Warning: .env file not found. Using default environment variables."
fi

# Check if MongoDB is running
echo "Checking MongoDB connection..."
if command -v mongo &> /dev/null; then
    mongo --eval "db.adminCommand('ismaster')" --quiet
    if [ $? -eq 0 ]; then
        echo "✓ MongoDB is running"
    else
        echo "⚠ MongoDB is not accessible. Make sure it's running on the configured URL."
    fi
else
    echo "⚠ MongoDB client not found. Assuming MongoDB is running remotely."
fi

# Check if Redis is running (optional)
if [ ! -z "$REDIS_URL" ]; then
    echo "Redis URL configured. Testing connection..."
    if command -v redis-cli &> /dev/null; then
        redis-cli -u $REDIS_URL ping > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo "✓ Redis is running"
        else
            echo "⚠ Redis is not accessible. Will use in-memory fallback."
        fi
    else
        echo "⚠ Redis client not found. Will use in-memory fallback."
    fi
fi

# Start the FastAPI server
echo "Starting FastAPI server..."
echo "Server will be available at: http://localhost:${PORT:-8001}"
echo "API docs will be available at: http://localhost:${PORT:-8001}/docs"
echo ""
python server.py
