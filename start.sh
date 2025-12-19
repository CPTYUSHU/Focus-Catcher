#!/bin/bash

# Main startup script for FastAPI Agentic Loop application
# This script loads environment variables and starts the server

# Change to script directory
cd "$(dirname "$0")"

# Check if API key is set
if [ -z "$SUPER_MIND_API_KEY" ]; then
    # Try to load from .env file
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
        echo "✅ Loaded environment variables from .env file"
    else
        echo "⚠️  WARNING: SUPER_MIND_API_KEY environment variable is not set!"
        echo ""
        echo "Please set it before running:"
        echo "  export SUPER_MIND_API_KEY='your_api_key_here'"
        echo ""
        echo "Or create a .env file with:"
        echo "  SUPER_MIND_API_KEY=your_api_key_here"
        echo ""
        echo "Starting server anyway (API calls will fail without valid key)..."
        echo ""
    fi
fi

# Run the FastAPI application in development mode
echo "🚀 Starting FastAPI server..."
uvicorn main:app --reload --host 127.0.0.1 --port 8000

