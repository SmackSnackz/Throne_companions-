#!/bin/bash

# Development server with hot reload

echo "Starting Throne Companions Backend in development mode..."
echo "Hot reload enabled - changes will automatically restart the server"
echo ""

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Start with uvicorn and reload
uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001} --reload
