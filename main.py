from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import requests
import json
from bs4 import BeautifulSoup
import re
import google.generativeai as genai

# Import database models
from database import get_db, init_db, Session as DBSession, Capture

# Import AI prompts
from focus_prompts import (
    SESSION_ANALYSIS_PROMPT,
    LEARNING_GUIDE_PROMPT,
    format_captures_for_analysis
)

# Try to load environment variables from .env file (ignore if file doesn't exist or can't be read)
try:
    from dotenv import load_dotenv
    load_dotenv(override=False)
except Exception as e:
    print(f"Note: Could not load .env file: {e}")
    print("Using environment variables from system instead.")

# Initialize FastAPI app
app = FastAPI(title="Chat API with Focus Catcher", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized")

# Add CORS middleware to allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client will be initialized lazily
_client = None


def get_openai_client():
    """Get or create OpenAI client instance."""
    global _client
    if _client is None:
        api_key = os.getenv("SUPER_MIND_API_KEY")
        if not api_key:
            raise ValueError(
                "SUPER_MIND_API_KEY environment variable is not set. "
                "Please set it in your environment or create a .env file."
            )
        _client = OpenAI(
            api_key=api_key,
            base_url="https://space.ai-builders.com/backend/v1"
        )
    return _client


def get_gemini_model():
    """Get or create Gemini model instance."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is not set. "
            "Please set it in your environment or create a .env file."
        )
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')  # 使用最新最快的模型


def print_message_history(messages: list):
    """
    Print the complete message history for debugging.
    Shows the full conversation flow including tool calls and results.
    """
    print("\n" + "="*80)
    print("📋 COMPLETE MESSAGE HISTORY (DEBUG)")
    print("="*80)
    
    for idx, msg in enumerate(messages, 1):
        role = msg.get("role", "unknown")
        
        print(f"\n[Message {idx}] Role: {role.upper()}")
        print("-" * 80)
        
        if role == "user":
            # User message
            content = msg.get("content", "")
            print(f"Content: {content}")
            
        elif role == "assistant":
            # Assistant message (may have tool_calls or content)
            content = msg.get("content")
            tool_calls = msg.get("tool_calls")
            
            if content:
                print(f"Content: {content}")
            else:
                print(f"Content: None")
            
            if tool_calls:
                print(f"\nTool Calls: {len(tool_calls)} call(s)")
                for tc_idx, tc in enumerate(tool_calls, 1):
                    func_name = tc.get("function", {}).get("name", "unknown")
                    func_args = tc.get("function", {}).get("arguments", "{}")
                    tc_id = tc.get("id", "unknown")
                    
                    print(f"  [{tc_idx}] Function: {func_name}")
                    print(f"      ID: {tc_id}")
                    print(f"      Arguments: {func_args}")
                    
        elif role == "tool":
            # Tool result
            tool_call_id = msg.get("tool_call_id", "unknown")
            content = msg.get("content", "")
            
            print(f"Tool Call ID: {tool_call_id}")
            
            # Try to parse and pretty-print JSON content
            try:
                content_obj = json.loads(content)
                
                # Check if it's an error
                if "error" in content_obj:
                    print(f"Result: ERROR - {content_obj['error']}")
                else:
                    # For successful results, show a summary
                    if "url" in content_obj:
                        # read_page result
                        print(f"Result Type: read_page")
                        print(f"  URL: {content_obj.get('url', 'N/A')}")
                        print(f"  Title: {content_obj.get('title', 'N/A')}")
                        print(f"  Content Length: {content_obj.get('length', 0)} chars")
                        print(f"  Content Preview: {content_obj.get('content', '')[:100]}...")
                    elif "queries" in content_obj:
                        # web_search result
                        print(f"Result Type: web_search")
                        queries = content_obj.get("queries", [])
                        print(f"  Number of queries: {len(queries)}")
                        if queries:
                            first_query = queries[0]
                            print(f"  First query keyword: {first_query.get('keyword', 'N/A')}")
                    else:
                        # Unknown format, show first 200 chars
                        print(f"Result: {content[:200]}...")
                        
            except (json.JSONDecodeError, Exception):
                # Not JSON or parsing failed, show raw content
                print(f"Result (raw): {content[:200]}...")
        
        elif role == "system":
            # System message
            content = msg.get("content", "")
            print(f"Content: {content}")
        
        else:
            # Unknown role
            print(f"Content: {msg}")
    
    print("\n" + "="*80)
    print("📋 END OF MESSAGE HISTORY")
    print("="*80 + "\n")


def web_search(query: str) -> dict:
    """
    Perform a web search using the internal search API.
    
    Args:
        query: The search query string
        
    Returns:
        dict: Search results from the API
        
    Raises:
        Exception: If the API call fails
    """
    api_key = os.getenv("SUPER_MIND_API_KEY")
    if not api_key:
        raise ValueError("SUPER_MIND_API_KEY environment variable is not set.")
    
    url = "https://space.ai-builders.com/backend/v1/search/"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "keywords": [query],
        "max_results": 3
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Web search API call failed: {str(e)}")


def read_page(url: str) -> dict:
    """
    Fetch a web page and extract its main text content.
    
    Args:
        url: The URL of the page to read
        
    Returns:
        dict: Contains the URL, title, and extracted text content
        
    Raises:
        Exception: If the page cannot be fetched or parsed
    """
    try:
        # Fetch the page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get title
        title = soup.title.string if soup.title else "No title"
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to avoid overwhelming the LLM
        max_length = 8000
        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated due to length...]"
        
        return {
            "url": url,
            "title": title,
            "content": text,
            "length": len(text)
        }
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch page: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse page: {str(e)}")


# Tool schema for LLM to understand available functions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information. Use this when you need up-to-date information about events, facts, or topics that may have changed recently. Returns relevant search results from the internet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string. Be specific and use keywords that will return relevant results."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_page",
            "description": "Fetch and read the content of a specific web page. Use this when you have a URL and need to extract detailed information from that page. Returns the page title and main text content with scripts, styles, and navigation removed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL of the web page to read (must include http:// or https://)"
                    }
                },
                "required": ["url"]
            }
        }
    }
]


# Request model
class ChatRequest(BaseModel):
    user_message: str


# Response model
class ChatResponse(BaseModel):
    content: str
    tool_calls: list | None = None  # Optional field to show tool calls made by LLM


# ============================================================
# Focus Catcher Models
# ============================================================

class CaptureRequest(BaseModel):
    """Request model for capturing a learning focus point."""
    selected_text: str
    page_url: str
    page_title: str | None = None


class CaptureResponse(BaseModel):
    """Response model for capture endpoint."""
    success: bool
    capture_id: int
    session_id: int
    message: str


class SessionResponse(BaseModel):
    """Response model for session information."""
    id: int
    start_time: datetime
    end_time: datetime | None
    status: str
    capture_count: int


@app.get("/api")
async def root():
    """Root endpoint to verify the API is running."""
    return {"message": "Chat API is running. Use POST /chat to send messages."}


# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend HTML page."""
    return FileResponse("frontend/index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with full Agentic Loop implementation.
    The LLM can call tools, receive results, and iterate up to max_turns times.
    
    Args:
        request: ChatRequest containing user_message field
        
    Returns:
        ChatResponse containing the assistant's final response and tool call history
    """
    max_turns = 10  # Maximum number of agent turns to prevent infinite loops (increased from 5)
    
    try:
        # Get OpenAI client
        client = get_openai_client()
        
        # Initialize conversation history
        messages = [
            {"role": "user", "content": request.user_message}
        ]
        
        # Track all tool calls made during the conversation
        all_tool_calls = []
        
        # Track consecutive empty responses
        consecutive_empty_responses = 0
        
        # Track consecutive tool-only turns (no text generation)
        consecutive_tool_turns = 0
        
        print(f"\n{'='*60}")
        print(f"[User] {request.user_message}")
        print(f"{'='*60}")
        
        # Agentic Loop: iterate up to max_turns
        for turn in range(max_turns):
            print(f"\n[Turn {turn + 1}/{max_turns}]")
            
            # Call LLM with current conversation history
            response = client.chat.completions.create(
                model="gpt-5",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
            
            # Extract the assistant's response
            message = response.choices[0].message
            
            # Add assistant's message to conversation history
            # Convert to dict format for messages array
            # Note: content can be None when tool_calls are present
            assistant_message = {
                "role": "assistant",
                "content": message.content if message.content else None
            }
            
            # Check if the model wants to call tools
            if message.tool_calls:
                # Increment consecutive tool turns counter
                consecutive_tool_turns += 1
                
                # Check if we've had too many consecutive tool calls
                if consecutive_tool_turns >= 5:
                    # LLM is stuck in a search loop - force it to generate an answer
                    print(f"[Agent] Warning: {consecutive_tool_turns} consecutive tool calls detected")
                    print(f"[Agent] Forcing answer generation to break the loop...")
                    
                    # Add a strong directive
                    messages.append({
                        "role": "system",
                        "content": "你已经搜索了足够多的信息。现在必须停止搜索，基于已获取的所有搜索结果生成一个完整的回答。即使搜索结果中没有直接答案，你也要总结链接、标题等信息，或者告诉用户你找到了哪些相关资源。不要再调用任何工具。"
                    })
                    
                    # Call LLM without tools
                    try:
                        final_response = client.chat.completions.create(
                            model="gpt-5",
                            messages=messages,
                            tools=None,
                            temperature=0.7
                        )
                        
                        final_message = final_response.choices[0].message
                        final_answer = final_message.content or "抱歉，虽然我进行了多次搜索，但无法生成满意的回答。建议您直接访问相关新闻网站获取最新信息。"
                        
                        print(f"[Agent] Forced Final Answer: {final_answer}")
                        print(f"{'='*60}\n")
                        
                        messages.append({
                            "role": "assistant",
                            "content": final_answer
                        })
                        
                        print_message_history(messages)
                        
                        return ChatResponse(
                            content=final_answer,
                            tool_calls=all_tool_calls if all_tool_calls else None
                        )
                    except Exception as e:
                        print(f"[Error] Failed to force answer: {e}")
                        # Continue to normal flow
                
                # Check if this is the last turn
                if turn == max_turns - 1:
                    # Last turn but LLM still wants to call tools
                    # Force it to generate an answer instead
                    print(f"[Agent] Warning: Last turn reached, but LLM wants to call {len(message.tool_calls)} tool(s)")
                    print(f"[Agent] Forcing final answer generation...")
                    
                    # Add a system message to force answer generation
                    messages.append({
                        "role": "system",
                        "content": "这是最后一轮对话。请基于已获取的信息生成最终答案，不要再调用工具。如果信息不足，请说明并给出部分答案。"
                    })
                    
                    # Call LLM again without tools to force text generation
                    final_response = client.chat.completions.create(
                        model="gpt-5",
                        messages=messages,
                        tools=None,  # Disable tools
                        temperature=0.7
                    )
                    
                    final_message = final_response.choices[0].message
                    final_answer = final_message.content or "抱歉，我无法生成完整的回答。请尝试简化您的问题。"
                    
                    print(f"[Agent] Forced Final Answer: {final_answer}")
                    print(f"{'='*60}\n")
                    
                    # Add final message to history
                    messages.append({
                        "role": "assistant",
                        "content": final_answer
                    })
                    
                    print_message_history(messages)
                    
                    return ChatResponse(
                        content=final_answer,
                        tool_calls=all_tool_calls if all_tool_calls else None
                    )
                
                print(f"[Agent] Decided to call {len(message.tool_calls)} tool(s)")
                print(f"[Agent] Consecutive tool-only turns: {consecutive_tool_turns}")
                
                # Reset empty response counter (we got tool calls)
                consecutive_empty_responses = 0
                
                # Add tool_calls to assistant message
                # Fix: Ensure content is empty string instead of None to avoid API errors
                if assistant_message["content"] is None:
                    assistant_message["content"] = ""
                
                assistant_message["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
                messages.append(assistant_message)
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Agent] Calling tool: '{function_name}'")
                    print(f"[Agent] Arguments: {function_args}")
                    
                    # Track this tool call
                    all_tool_calls.append({
                        "id": tool_call.id,
                        "function": function_name,
                        "arguments": function_args
                    })
                    
                    # Execute the tool
                    try:
                        if function_name == "web_search":
                            query = function_args.get("query", "")
                            tool_result = web_search(query)
                            
                            # Format the result for display
                            result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
                            print(f"[System] Tool Output: {result_str[:200]}..." if len(result_str) > 200 else f"[System] Tool Output: {result_str}")
                            
                            # Add tool result to conversation history
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_str
                            })
                            
                        elif function_name == "read_page":
                            url = function_args.get("url", "")
                            tool_result = read_page(url)
                            
                            # Format the result for display
                            result_str = json.dumps(tool_result, ensure_ascii=False, indent=2)
                            print(f"[System] Tool Output (read_page):")
                            print(f"[System]   URL: {tool_result.get('url', 'N/A')}")
                            print(f"[System]   Title: {tool_result.get('title', 'N/A')}")
                            print(f"[System]   Content length: {tool_result.get('length', 0)} characters")
                            print(f"[System]   Preview: {tool_result.get('content', '')[:150]}...")
                            
                            # Add tool result to conversation history
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_str
                            })
                            
                        else:
                            error_msg = f"Unknown tool: {function_name}"
                            print(f"[System] Error: {error_msg}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps({"error": error_msg})
                            })
                    
                    except Exception as e:
                        error_msg = f"Tool execution failed: {str(e)}"
                        print(f"[System] Error: {error_msg}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": error_msg})
                        })
                
                # Continue to next turn to let LLM process the tool results
                continue
            
            # No tool calls - check if we have a final answer
            elif message.content:
                # LLM has provided final answer with content
                messages.append(assistant_message)
                
                # Reset counters
                consecutive_empty_responses = 0
                consecutive_tool_turns = 0
                
                final_answer = message.content
                print(f"[Agent] Final Answer: {final_answer}")
                print(f"{'='*60}\n")
                
                # DEBUG: Print complete message history before returning
                print_message_history(messages)
                
                return ChatResponse(
                    content=final_answer,
                    tool_calls=all_tool_calls if all_tool_calls else None
                )
            
            else:
                # No tool calls AND no content - this is unusual
                # This might happen if the LLM returns an empty response
                
                consecutive_empty_responses += 1
                
                print(f"[Agent] Warning: Received response with no tool calls and no content")
                print(f"[Agent] Consecutive empty responses: {consecutive_empty_responses}")
                print(f"[Agent] Turn {turn + 1}/{max_turns}: Attempting to recover...")
                
                # If we've had 2+ consecutive empty responses, force a final answer
                if consecutive_empty_responses >= 2 or turn == max_turns - 1:
                    print(f"[Agent] Too many empty responses or last turn - forcing final answer...")
                    
                    # Add a strong directive to generate an answer
                    messages.append({
                        "role": "system",
                        "content": "你必须立即生成一个回答。请基于之前获取的任何信息回答用户的问题。如果没有足够信息，请诚实地告诉用户你无法获取准确信息，但尽量提供一些相关建议。不要返回空响应。"
                    })
                    
                    # Call LLM one more time without tools to force text generation
                    try:
                        final_response = client.chat.completions.create(
                            model="gpt-5",
                            messages=messages,
                            tools=None,  # Disable tools
                            temperature=0.7
                        )
                        
                        final_message = final_response.choices[0].message
                        final_answer = final_message.content or "抱歉，我在处理您的问题时遇到了困难。我已经尝试搜索相关信息，但无法生成完整的回答。请尝试重新表述您的问题，或将其分解成更简单的部分。"
                        
                        print(f"[Agent] Forced Final Answer: {final_answer}")
                        print(f"{'='*60}\n")
                        
                        messages.append({
                            "role": "assistant",
                            "content": final_answer
                        })
                        
                        print_message_history(messages)
                        
                        return ChatResponse(
                            content=final_answer,
                            tool_calls=all_tool_calls if all_tool_calls else None
                        )
                    except Exception as e:
                        print(f"[Error] Failed to force final answer: {e}")
                        final_answer = "抱歉，我在生成回答时遇到了问题。请尝试重新表述您的问题，或将问题分解成更简单的部分。"
                        
                        print_message_history(messages)
                        
                        return ChatResponse(
                            content=final_answer,
                            tool_calls=all_tool_calls if all_tool_calls else None
                        )
                
                # First empty response - add a guidance prompt
                messages.append({
                    "role": "system",
                    "content": "请基于已获取的搜索结果，生成一个完整的回答。如果搜索结果中包含相关信息，请提取并总结。如果信息不足，请说明并给出部分答案。"
                })
                
                print(f"[Agent] Added guidance prompt, retrying...")
                
                # Continue to next turn with the guidance
                continue
        
        # Max turns reached without final answer
        print(f"[System] Max turns ({max_turns}) reached")
        print(f"{'='*60}\n")
        
        # DEBUG: Print complete message history before returning
        print_message_history(messages)
        
        return ChatResponse(
            content="I apologize, but I've reached the maximum number of steps. Please try rephrasing your question.",
            tool_calls=all_tool_calls if all_tool_calls else None
        )
        
    except ValueError as e:
        # Handle missing API key
        print(f"[Error] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    except Exception as e:
        # Handle any errors that occur during the API call
        print(f"[Error] {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error in agentic loop: {str(e)}"
        )


# ============================================================
# Focus Catcher Endpoints
# ============================================================

def detect_topic_shift(new_text: str, recent_captures: list, db: Session) -> tuple[bool, str]:
    """
    Use AI to detect if the new capture represents a topic shift.
    
    Args:
        new_text: The newly captured text
        recent_captures: List of recent Capture objects (last 3-5)
        db: Database session
    
    Returns:
        (topic_shifted: bool, new_topic: str)
    """
    if len(recent_captures) < 3:
        # Not enough data to determine topic shift
        return False, ""
    
    try:
        # Prepare context from recent captures
        recent_texts = "\n\n".join([
            f"捕捉 {i+1}: {cap.selected_text[:200]}"
            for i, cap in enumerate(recent_captures[:3])
        ])
        
        # Create prompt for topic detection
        prompt = f"""你是一个学习主题识别助手。请分析用户的学习捕捉内容，判断新捕捉是否与之前的主题相关。

最近的捕捉内容：
{recent_texts}

新的捕捉内容：
{new_text[:200]}

请分析：
1. 新捕捉的主题是什么？
2. 它与之前的捕捉是否属于同一学习主题？

判断标准：
- 如果是同一技术栈、同一问题领域、或相关概念 → 相关
- 如果是完全不同的领域、技术或话题 → 不相关

请用 JSON 格式回答：
{{
  "related": true/false,
  "new_topic": "新主题的简短描述（如果不相关）",
  "confidence": 0.0-1.0,
  "reason": "判断理由"
}}"""

        # Call Gemini for fast analysis
        gemini_model = get_gemini_model()
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        )
        
        result = json.loads(response.text)
        
        is_related = result.get("related", True)
        new_topic = result.get("new_topic", "")
        confidence = result.get("confidence", 0.5)
        reason = result.get("reason", "")
        
        print(f"[Topic Detection] Related: {is_related}, Confidence: {confidence:.2f}")
        print(f"[Topic Detection] Reason: {reason}")
        
        if not is_related and confidence > 0.6:
            print(f"[Topic Detection] 🔄 Topic shift detected: {new_topic}")
            return True, new_topic
        
        return False, ""
        
    except Exception as e:
        print(f"[Topic Detection] Error: {e}")
        # On error, assume no topic shift (fail safe)
        return False, ""


def get_or_create_active_session(db: Session, new_capture_text: str = None) -> tuple[DBSession, bool, str]:
    """
    Get the current active session or create a new one based on topic detection.
    
    Args:
        db: Database session
        new_capture_text: The text being captured (for topic detection)
    
    Returns:
        (session, topic_shifted, new_topic)
    """
    # Find the most recent active session
    latest_session = db.query(DBSession).filter(
        DBSession.status == "active"
    ).order_by(DBSession.start_time.desc()).first()
    
    # If no active session exists, create one
    if not latest_session:
        new_session = DBSession(
            start_time=datetime.utcnow(),
            status="active",
            core_goal="新学习会话"
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        print(f"[Focus Catcher] Created first session: {new_session.id}")
        return new_session, False, ""
    
    # If we have a new capture text, check for topic shift
    if new_capture_text:
        # Get recent captures from the current session
        recent_captures = db.query(Capture).filter(
            Capture.session_id == latest_session.id
        ).order_by(Capture.timestamp.desc()).limit(5).all()
        
        # Detect topic shift
        topic_shifted, new_topic = detect_topic_shift(new_capture_text, recent_captures, db)
        
        if topic_shifted:
            # Mark current session as completed
            latest_session.status = "completed"
            latest_session.end_time = datetime.utcnow()
            db.commit()
            
            # Create new session for the new topic
            new_session = DBSession(
                start_time=datetime.utcnow(),
                status="active",
                core_goal=new_topic
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            print(f"[Focus Catcher] 🔄 Topic shift! Created new session #{new_session.id}: {new_topic}")
            return new_session, True, new_topic
    
    # Continue with current session
    return latest_session, False, ""


@app.post("/api/focus/capture", response_model=CaptureResponse)
async def capture_focus(request: CaptureRequest, db: Session = Depends(get_db)):
    """
    Capture a learning focus point with intelligent topic detection.
    This endpoint uses AI to detect topic shifts and automatically create new sessions.
    
    Args:
        request: CaptureRequest containing selected_text, page_url, page_title
        db: Database session
    
    Returns:
        CaptureResponse with success status, IDs, and topic shift information
    """
    try:
        start_time = datetime.utcnow()
        
        # Get or create active session with topic detection
        session, topic_shifted, new_topic = get_or_create_active_session(db, request.selected_text)
        
        # Create capture record
        capture = Capture(
            session_id=session.id,
            selected_text=request.selected_text,
            page_url=request.page_url,
            page_title=request.page_title,
            timestamp=datetime.utcnow()
        )
        
        db.add(capture)
        db.commit()
        db.refresh(capture)
        
        # Update session capture count
        capture_count = db.query(Capture).filter(
            Capture.session_id == session.id
        ).count()
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Build response message
        if topic_shifted:
            message = f"🔄 检测到新主题：{new_topic}，已创建新会话 #{session.id}"
        else:
            message = f"✅ 已捕捉到会话 #{session.id}"
        
        print(f"[Focus Catcher] Captured focus point #{capture.id} in session #{session.id}")
        print(f"[Focus Catcher] Response time: {response_time:.2f}ms")
        print(f"[Focus Catcher] Text preview: {request.selected_text[:100]}...")
        
        # Check if we should trigger batch analysis (5-10 captures)
        if capture_count >= 5:
            print(f"[Focus Catcher] 🎯 Session has {capture_count} captures - ready for AI analysis")
        
        return CaptureResponse(
            success=True,
            capture_id=capture.id,
            session_id=session.id,
            message=message
        )
        
    except Exception as e:
        print(f"[Focus Catcher] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to capture: {str(e)}"
        )


@app.get("/api/focus/sessions")
async def get_sessions(db: Session = Depends(get_db)):
    """
    Get all learning sessions with capture counts.
    """
    try:
        sessions = db.query(DBSession).order_by(DBSession.start_time.desc()).all()
        
        result = []
        for session in sessions:
            capture_count = db.query(Capture).filter(Capture.session_id == session.id).count()
            result.append({
                "id": session.id,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "status": session.status,
                "capture_count": capture_count
            })
        
        return {"sessions": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get sessions: {str(e)}"
        )


@app.get("/api/focus/captures/{session_id}")
async def get_captures(session_id: int, db: Session = Depends(get_db)):
    """
    Get all captures for a specific session.
    """
    try:
        captures = db.query(Capture).filter(
            Capture.session_id == session_id
        ).order_by(Capture.timestamp.asc()).all()
        
        result = []
        for capture in captures:
            result.append({
                "id": capture.id,
                "selected_text": capture.selected_text,
                "page_url": capture.page_url,
                "page_title": capture.page_title,
                "timestamp": capture.timestamp.isoformat(),
                "focus_point": capture.focus_point,
                "content_type": capture.content_type,
                "suggested_action": capture.suggested_action
            })
        
        return {"captures": result}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get captures: {str(e)}"
        )


@app.delete("/api/focus/sessions/{session_id}")
async def delete_session(session_id: int, db: Session = Depends(get_db)):
    """
    Delete a learning session and all its captures.
    
    Args:
        session_id: The session ID to delete
        db: Database session
    
    Returns:
        Success message
    """
    try:
        # Check if session exists
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get capture count before deletion
        capture_count = db.query(Capture).filter(Capture.session_id == session_id).count()
        
        # Delete all captures for this session
        db.query(Capture).filter(Capture.session_id == session_id).delete()
        
        # Delete the session
        db.delete(session)
        db.commit()
        
        print(f"[Focus Catcher] 🗑️ Deleted session #{session_id} with {capture_count} captures")
        
        return {
            "success": True,
            "message": f"Session #{session_id} and {capture_count} captures deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"[Focus Catcher] Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@app.post("/api/focus/analyze/{session_id}")
def analyze_session(session_id: int, db: Session = Depends(get_db)):
    """
    Analyze a learning session using AI.
    Generate insights about learning goals, main threads, branches, and action guide.
    
    Args:
        session_id: The session ID to analyze
        db: Database session
    
    Returns:
        Analysis results including core goal, main thread, branches, and action guide
    """
    try:
        # Get session
        session = db.query(DBSession).filter(DBSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get all captures for this session
        captures = db.query(Capture).filter(
            Capture.session_id == session_id
        ).order_by(Capture.timestamp.asc()).all()
        
        if len(captures) == 0:
            raise HTTPException(status_code=400, detail="Session has no captures to analyze")
        
        print(f"\n{'='*60}")
        print(f"[Focus Catcher] 🤖 Starting AI analysis for session #{session_id}")
        print(f"[Focus Catcher] Captures to analyze: {len(captures)}")
        print(f"{'='*60}\n")
        
        # Format captures for analysis
        captures_data = []
        for capture in captures:
            captures_data.append({
                'id': capture.id,
                'timestamp': capture.timestamp.isoformat(),
                'selected_text': capture.selected_text,
                'page_title': capture.page_title,
                'page_url': capture.page_url
            })
        
        captures_text = format_captures_for_analysis(captures_data)
        
        # Prepare analysis prompt
        analysis_prompt = SESSION_ANALYSIS_PROMPT.format(
            session_id=session_id,
            start_time=session.start_time.isoformat(),
            capture_count=len(captures),
            captures_list=captures_text
        )
        
        # Call LLM for analysis
        USE_MOCK_DATA = False  # 使用 Google Gemini API
        
        if USE_MOCK_DATA:
            print("[Focus Catcher] 🧪 Using mock data for testing...")
            
            # 使用固定的测试数据
            analysis_json = {
                "core_goal": "学习和验证 Focus Catcher 的核心功能，包括捕捉速度、会话分组和 AI 分析能力",
                "main_thread": [
                    "验证捕捉功能的响应速度是否达标（目标 < 200ms）",
                    "测试 15 分钟会话分组逻辑是否合理",
                    "验证批量分析触发机制（5-10 条触发）"
                ],
                "branches": [
                    "探索 Chrome 插件的实现方案",
                    "研究 AI Prompt 的优化策略",
                    "思考真实学习场景的应用"
                ],
                "understood": [
                    "捕捉功能工作正常，响应时间平均 14ms，远超预期",
                    "会话自动分组功能正常，15 分钟规则生效",
                    "批量分析触发提示已正确显示"
                ],
                "unclear": [
                    "AI 分析的准确性和实用性如何",
                    "在真实学习场景中的体验如何",
                    "Chrome 插件的快捷键是否真的够丝滑"
                ],
                "action_guide": [
                    "完成 AI 分析功能的 LLM 调用修复",
                    "开发 Chrome 插件原型，验证快捷键体验",
                    "在真实学习场景中测试捕捉功能",
                    "收集使用反馈，迭代优化产品"
                ],
                "learning_pattern": "系统化测试驱动 - 你采用了逐步验证每个功能模块的方法，这确保了产品的稳定性和可靠性"
            }
            
            print("[Focus Catcher] ✅ Mock data loaded")
            
        else:
            # 使用 Google Gemini API
            model = get_gemini_model()
            
            print("[Focus Catcher] 🧠 Calling Gemini for deep analysis...")
            
            # 准备捕捉内容摘要
            captures_summary = "\n".join([
                f"{idx+1}. {c['selected_text'][:200]}" 
                for idx, c in enumerate(captures_data)
            ])
            
            user_prompt = f"""你是一个学习路径分析专家。请分析以下 {len(captures_data)} 条学习捕捉记录，识别用户的学习目标和模式。

学习捕捉记录：
{captures_summary}

请返回 JSON 格式的分析结果，包含以下字段：
- core_goal: 核心学习目标（字符串，简洁描述用户在学什么）
- main_thread: 主线问题（字符串数组，2-3个核心关注点）
- branches: 分支问题（字符串数组，1-3个延伸或相关问题）
- understood: 已经理解的部分（字符串数组，1-3个要点）
- unclear: 还需要弄清楚的问题（字符串数组，1-3个问题）
- action_guide: 下一步学习建议（字符串数组，3-5个具体可执行的步骤）
- learning_pattern: 学习模式观察（字符串，例如：深度优先、广度优先、问题驱动等）

只返回 JSON，不要其他内容。"""
            
            print(f"[Focus Catcher] Prompt length: {len(user_prompt)} chars")
            
            try:
                response = model.generate_content(user_prompt)
                analysis_result = response.text
                
                print(f"[Focus Catcher] ✅ Gemini response received")
                print(f"[Focus Catcher] Response length: {len(analysis_result)} chars")
                print(f"[Focus Catcher] Response preview:")
                print("="*80)
                print(analysis_result[:500] if analysis_result else "(None or empty)")
                print("="*80)
                
                # Parse JSON result
                try:
                    # 尝试直接解析
                    analysis_json = json.loads(analysis_result)
                    print("[Focus Catcher] ✅ JSON parsed successfully")
                    
                    # 清理 HTML 标签（如 <br>、<br/>）
                    def clean_html_tags(text):
                        """移除 HTML 标签，保持纯文本"""
                        if isinstance(text, str):
                            # 移除 <br>、<br/>、<br />
                            text = re.sub(r'<br\s*/?>',  '\n', text, flags=re.IGNORECASE)
                            # 移除其他 HTML 标签
                            text = re.sub(r'<[^>]+>', '', text)
                            # 清理多余的空白
                            text = re.sub(r'\n\s*\n', '\n', text)
                            text = text.strip()
                        return text
                    
                    # 递归清理 JSON 中的所有字符串
                    def clean_json_strings(obj):
                        if isinstance(obj, dict):
                            return {k: clean_json_strings(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [clean_json_strings(item) for item in obj]
                        elif isinstance(obj, str):
                            return clean_html_tags(obj)
                        return obj
                    
                    analysis_json = clean_json_strings(analysis_json)
                    print("[Focus Catcher] ✅ HTML tags cleaned")
                except json.JSONDecodeError as e:
                    print(f"[Focus Catcher] ❌ JSON parse error: {e}")
                    print(f"[Focus Catcher] Attempting regex extraction...")
                    
                    # 尝试提取 JSON（Gemini 可能会在 JSON 前后加文字）
                    json_match = re.search(r'\{.*\}', analysis_result, re.DOTALL)
                    if json_match:
                        try:
                            analysis_json = json.loads(json_match.group())
                            print("[Focus Catcher] ✅ JSON extracted via regex")
                        except:
                            raise ValueError(f"Failed to parse extracted JSON: {json_match.group()[:200]}")
                    else:
                        raise ValueError(f"No JSON found in response: {analysis_result[:200]}")
                        
            except Exception as e:
                print(f"[Focus Catcher] ❌ Gemini API error: {e}")
                raise ValueError(f"Gemini API call failed: {str(e)}")
        
        # Generate user-friendly learning guide
        print("[Focus Catcher] 📝 Generating learning guide...")
        
        if USE_MOCK_DATA:
            # 使用固定的学习指南
            learning_guide = """# 🎯 你的学习主线

你正在系统化地测试和验证 **Focus Catcher** 的核心功能。这是一个非常扎实的方法！

## 📚 你正在探索的问题

### 主要问题
• 捕捉功能的响应速度是否达标（目标 < 200ms）
• 15 分钟会话分组逻辑是否合理
• 批量分析触发机制（5-10 条触发）是否正常

### 延伸问题
• Chrome 插件的实现方案
• AI Prompt 的优化策略
• 真实学习场景的应用

## ✅ 你已经理解的部分

• **捕捉速度超预期** - 响应时间平均 14ms，远低于 200ms 目标
• **会话分组正常** - 15 分钟规则生效，自动创建新会话
• **触发机制正确** - 达到 5 条时正确显示分析按钮

## 🤔 还需要弄清楚的

- [ ] AI 分析的准确性和实用性
- [ ] 真实学习场景中的体验
- [ ] Chrome 插件快捷键是否足够丝滑

## 🚀 建议的下一步

1. **修复 AI 分析功能** - 解决 LLM 调用的 bug，尝试简化 Prompt 或使用 JSON mode
2. **开发 Chrome 插件原型** - 验证快捷键体验，在真实网页中测试
3. **真实场景测试** - 在日常学习中使用，收集真实反馈
4. **迭代优化** - 根据反馈改进产品

## 💡 学习模式观察

你采用了**系统化测试驱动**的方法 - 逐步验证每个功能模块。这种方法确保了产品的稳定性和可靠性。继续保持这种严谨的态度！

---

**加油！你已经完成了 90% 的核心功能。** 🎉
"""
            print("[Focus Catcher] ✅ Mock learning guide loaded")
            
        else:
            # 直接使用分析结果生成简洁的回顾指南（不调用 Gemini）
            print("[Focus Catcher] 📝 Generating learning guide...")
            
            try:
                # 格式化原文内容
                original_texts = []
                for idx, capture in enumerate(captures_data, 1):
                    # 截取前 150 字符，如果太长则添加省略号
                    text = capture['selected_text']
                    if len(text) > 150:
                        text = text[:150] + '...'
                    original_texts.append(f"{idx}. {text}")
                
                # 使用纯文本模板，不包含任何 Markdown 符号
                learning_guide = f"""🎯 核心主题
{analysis_json.get('core_goal', '正在学习中...')}

📚 关键信息点
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('main_thread', []))])}

🔗 内容脉络
{chr(10).join(analysis_json.get('branches', []))}

✅ 已覆盖的内容
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('understood', []))])}

❓ 可能需要进一步查阅
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('unclear', []))])}

💡 回顾建议
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('action_guide', []))])}

📊 内容特点
{analysis_json.get('learning_pattern', '继续保持学习的节奏')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 原文回顾（共 {len(captures_data)} 条捕捉）

{chr(10).join(original_texts)}"""
                
                print("[Focus Catcher] ✅ Learning guide generated (with original texts)")
                print(f"[Focus Catcher] Guide length: {len(learning_guide)} chars")
                print(f"[Focus Catcher] Included {len(captures_data)} original captures")
            except Exception as e:
                print(f"[Focus Catcher] ❌ Guide generation error: {e}")
                # 备用：使用简单的纯文本模板
                try:
                    original_texts = []
                    for idx, capture in enumerate(captures_data, 1):
                        text = capture['selected_text']
                        if len(text) > 150:
                            text = text[:150] + '...'
                        original_texts.append(f"{idx}. {text}")
                except:
                    original_texts = ["(无法加载原文)"]
                
                learning_guide = f"""🎯 核心主题
{analysis_json.get('core_goal', '正在学习中...')}

📚 关键信息点
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('main_thread', []))])}

✅ 已覆盖的内容
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('understood', []))])}

❓ 可能需要进一步查阅
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('unclear', []))])}

💡 回顾建议
{chr(10).join([f'{idx+1}. {item}' for idx, item in enumerate(analysis_json.get('action_guide', []))])}

📊 内容特点
{analysis_json.get('learning_pattern', '继续保持学习的节奏')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 原文回顾（共 {len(captures_data)} 条捕捉）

{chr(10).join(original_texts)}"""
        
        print("[Focus Catcher] ✅ Learning guide generated")
        
        # Update session with analysis results
        session.core_goal = analysis_json.get('core_goal', '')
        session.main_thread = json.dumps(analysis_json.get('main_thread', []), ensure_ascii=False)
        session.branches = json.dumps(analysis_json.get('branches', []), ensure_ascii=False)
        session.action_guide = learning_guide
        session.status = 'completed'  # Mark session as analyzed
        
        db.commit()
        
        print(f"[Focus Catcher] 💾 Analysis saved to database")
        print(f"{'='*60}\n")
        
        # Return results
        return {
            "success": True,
            "session_id": session_id,
            "analysis": {
                "core_goal": analysis_json.get('core_goal', ''),
                "main_thread": analysis_json.get('main_thread', []),
                "branches": analysis_json.get('branches', []),
                "understood": analysis_json.get('understood', []),
                "unclear": analysis_json.get('unclear', []),
                "action_guide": analysis_json.get('action_guide', []),
                "learning_pattern": analysis_json.get('learning_pattern', '')
            },
            "learning_guide": learning_guide,
            "capture_count": len(captures)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Focus Catcher] ❌ Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze session: {str(e)}"
        )


# Mount static files (CSS, JS) - must be done after all routes are defined
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

