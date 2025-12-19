#!/bin/bash

# Check if API key is set
if [ -z "$SUPER_MIND_API_KEY" ]; then
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

# Run the FastAPI application in development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000

