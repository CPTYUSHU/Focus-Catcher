# Tool Calling 功能说明

## 概述

已成功为 FastAPI 应用添加了网络搜索工具调用功能。LLM 现在可以自动判断何时需要调用 `web_search` 工具来获取实时信息。

## 实现的功能

### 1. Web Search 函数

定义在 `main.py` 第 40-72 行：

```python
def web_search(query: str) -> dict:
    """
    使用内部搜索 API 执行网络搜索
    
    Args:
        query: 搜索查询字符串
        
    Returns:
        dict: API 返回的搜索结果
    """
```

**API 详情：**
- URL: `https://space.ai-builders.com/backend/v1/search/`
- 方法: POST
- 请求头: `Authorization: Bearer {SUPER_MIND_API_KEY}`
- 请求体: `{"keywords": ["query_string"], "max_results": 3}`

### 2. 工具 Schema

定义在 `main.py` 第 76-94 行：

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information...",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query string..."
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

这个 schema 遵循 OpenAI 的函数调用格式，让 LLM 能够理解：
- 工具的名称和用途
- 需要什么参数
- 参数的类型和描述

### 3. 聊天端点更新

`/chat` 端点现在支持工具调用：

```python
response = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": request.user_message}],
    tools=TOOLS,
    tool_choice="auto"  # 让模型自动决定是否使用工具
)
```

**响应格式：**

当 LLM 决定调用工具时：
```json
{
    "content": "LLM wants to call tool: web_search with arguments: {'query': 'Super Bowl LIX winner'}",
    "tool_calls": [
        {
            "id": "call_xNfbHSUyUAluCVffbPVgdH88",
            "function": "web_search",
            "arguments": {
                "query": "Super Bowl LIX winner"
            }
        }
    ]
}
```

当不需要工具时：
```json
{
    "content": "4",
    "tool_calls": null
}
```

## 测试结果

### ✅ 需要搜索的问题（触发工具调用）

1. **"Who won the Super Bowl?"**
   - 工具调用: `web_search`
   - 参数: `{"query": "Super Bowl LIX winner"}`

2. **"What is the current weather in New York?"**
   - 工具调用: `web_search`
   - 参数: `{"query": "New York, NY current weather"}`

### ✅ 不需要搜索的问题（不触发工具调用）

1. **"What is 2 + 2?"**
   - 直接回答: `"4"`
   - 无工具调用

2. **"Explain what Python is."**
   - 直接回答: 关于 Python 的解释
   - 无工具调用

## 使用方法

### 通过 curl 测试

```bash
# 需要搜索的问题
curl -s -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Who won the Super Bowl?"}' | python3 -m json.tool

# 简单问题
curl -s -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "What is 2 + 2?"}' | python3 -m json.tool
```

### 通过测试脚本

```bash
python3 test_tool_calling.py
```

### 通过 Swagger UI

访问 http://127.0.0.1:8000/docs 使用交互式 API 文档进行测试。

## 当前状态

✅ **已完成：**
- `web_search` 函数定义
- 工具 schema 定义（JSON 格式）
- LLM 工具调用集成
- 验证 LLM 能够输出有效的工具调用

⏳ **待实现：**
- 完整的工具执行循环（实际调用 web_search 并返回结果给 LLM）
- 多轮对话支持
- 工具调用结果的处理和展示

## 技术细节

### LLM 如何决定使用工具

通过 `tool_choice="auto"` 参数，LLM 会根据以下因素自动决定：

1. **问题类型**：是否需要实时/最新信息
2. **知识截止日期**：问题是否超出训练数据范围
3. **确定性**：是否需要验证或查找具体事实

### 工具调用流程

1. 用户发送消息到 `/chat`
2. 消息连同工具 schema 发送给 LLM
3. LLM 分析是否需要使用工具
4. 如果需要：
   - LLM 返回 `tool_calls` 对象
   - 包含函数名和参数
5. 如果不需要：
   - LLM 直接返回文本回答

## 下一步

要实现完整的工具执行循环，需要：

1. 检测到工具调用时，实际执行 `web_search(query)`
2. 将搜索结果添加到对话历史
3. 再次调用 LLM，让它基于搜索结果生成最终答案
4. 返回最终答案给用户

这将在下一个迭代中实现。

