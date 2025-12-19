#!/usr/bin/env python3
"""
Test script to demonstrate the full Agentic Loop with tool execution.
Run from project root: python tests/test_agentic_loop.py
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
                print(f"     Query: {tool_call['arguments'].get('query', 'N/A')}")
        else:
            print("\n✓ Direct answer (no tools needed)")
        
        print(f"\n⏱️  Response time: {elapsed:.2f}s")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    print(f"{'='*70}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print(" " * 20 + "AGENTIC LOOP DEMONSTRATION")
    print("="*70)
    print("\nThis demonstrates the full agentic loop:")
    print("1. LLM decides if it needs tools")
    print("2. Tools are executed and results returned")
    print("3. LLM processes results and provides final answer")
    print("4. Loop can iterate up to 3 times for complex queries")
    
    # Test 1: Question requiring web search
    test_chat(
        "Who won the Super Bowl in 2025?",
        "Question requiring real-time search"
    )
    
    time.sleep(1)
    
    # Test 2: Simple question (no tools)
    test_chat(
        "What is 15 * 8?",
        "Simple calculation (no tools needed)"
    )
    
    time.sleep(1)
    
    # Test 3: Another search question
    test_chat(
        "Who is the current president of the United States?",
        "Current information query"
    )
    
    time.sleep(1)
    
    # Test 4: General knowledge (no tools)
    test_chat(
        "What is the capital of France?",
        "General knowledge (no tools needed)"
    )
    
    print("\n" + "="*70)
    print(" " * 25 + "TESTS COMPLETE!")
    print("="*70)
    print("\n💡 Tip: Check the server logs to see the detailed agentic loop execution:")
    print("   - [Agent] Decided to call tool: 'search'")
    print("   - [System] Tool Output: '...'")
    print("   - [Agent] Final Answer: '...'")
    print("\n")

