#!/usr/bin/env python3
"""
Test script to demonstrate tool calling functionality.
Run from project root: python tests/test_tool_calling.py
"""

import requests
import json
import sys
from pathlib import Path

# Add parent directory to path to allow imports if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = "http://127.0.0.1:8000/chat"

def test_chat(message: str):
    """Send a message to the chat API and display the response."""
    print(f"\n{'='*60}")
    print(f"User: {message}")
    print(f"{'='*60}")
    
    response = requests.post(
        API_URL,
        json={"user_message": message},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAssistant: {data['content']}")
        
        if data.get('tool_calls'):
            print("\n🔧 Tool Calls:")
            for tool_call in data['tool_calls']:
                print(f"  - Function: {tool_call['function']}")
                print(f"    Arguments: {json.dumps(tool_call['arguments'], indent=6)}")
                print(f"    Call ID: {tool_call['id']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Test questions that should trigger tool calls
    print("\n" + "="*60)
    print("Testing Tool Calling Functionality")
    print("="*60)
    
    # Questions that need web search
    test_chat("Who won the Super Bowl?")
    test_chat("What is the current weather in New York?")
    test_chat("Who is the current president of France?")
    
    # Questions that don't need web search
    test_chat("What is 2 + 2?")
    test_chat("Explain what Python is.")
    
    print("\n" + "="*60)
    print("Testing Complete!")
    print("="*60 + "\n")

