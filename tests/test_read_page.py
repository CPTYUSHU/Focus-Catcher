#!/usr/bin/env python3
"""
Test script to demonstrate the read_page tool.
Run from project root: python tests/test_read_page.py
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add parent directory to path to allow imports if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

API_URL = "http://127.0.0.1:8000/chat"

def test_chat(message: str, description: str = ""):
    """Send a message to the chat API and display the response."""
    print(f"\n{'='*70}")
    if description:
        print(f"Test: {description}")
    print(f"{'='*70}")
    print(f"User: {message}")
    print(f"{'-'*70}")
    
    start_time = time.time()
    response = requests.post(
        API_URL,
        json={"user_message": message},
        headers={"Content-Type": "application/json"}
    )
    elapsed = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAssistant: {data['content']}")
        
        if data.get('tool_calls'):
            print(f"\n🔧 Tools Used ({len(data['tool_calls'])} call(s)):")
            for i, tool_call in enumerate(data['tool_calls'], 1):
                print(f"  {i}. {tool_call['function']}")
                if 'query' in tool_call['arguments']:
                    print(f"     Query: {tool_call['arguments']['query']}")
                if 'url' in tool_call['arguments']:
                    print(f"     URL: {tool_call['arguments']['url']}")
        else:
            print("\n✓ Direct answer (no tools needed)")
        
        print(f"\n⏱️  Response time: {elapsed:.2f}s")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    print(f"{'='*70}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 20 + "MULTI-TOOL DEMONSTRATION")
    print("="*70)
    print("\nDemonstrating both web_search and read_page tools:")
    
    # Test 1: Just web search
    test_chat(
        "Who won the Super Bowl in 2025?",
        "Simple search query"
    )
    
    time.sleep(2)
    
    # Test 2: Search + Read (simplified version)
    test_chat(
        "Search for Python official website and tell me the URL",
        "Search only"
    )
    
    time.sleep(2)
    
    # Test 3: Direct read_page
    test_chat(
        "What is on the Python homepage at python.org?",
        "May trigger read_page"
    )
    
    print("\n" + "="*70)
    print(" " * 25 + "TESTS COMPLETE!")
    print("="*70)
    print("\n💡 Check server logs for detailed tool execution:")
    print("   [Agent] Calling tool: 'web_search'")
    print("   [Agent] Calling tool: 'read_page'")
    print("   [System] Tool Output (read_page): ...")
    print("\n")

