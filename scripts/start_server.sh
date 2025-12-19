#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from .env file"
else
    echo "⚠️  Warning: .env file not found"
fi

# Check if API key is set
if [ -z "$SUPER_MIND_API_KEY" ]; then
    echo "❌ ERROR: SUPER_MIND_API_KEY is not set!"
    echo "Please create a .env file with: SUPER_MIND_API_KEY=your_api_key_here"
    exit 1
fi

echo "🚀 Starting FastAPI server..."
uvicorn main:app --reload --host 127.0.0.1 --port 8000

