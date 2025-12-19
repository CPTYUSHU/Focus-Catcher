# Agentic Loop 实现文档

## 概述

已成功实现完整的 Agentic Loop（智能体循环），允许 LLM 自主决定何时调用工具、执行工具、处理结果，并迭代最多 3 次以处理复杂查询。

## 核心功能

### 1. 完整的工具执行循环

```
用户提问 → LLM 分析 → 决定是否需要工具
                ↓
                是 → 执行工具 → 获取结果 → 返回给 LLM
                ↓
                LLM 处理结果 → 生成最终答案
                ↓
                否 → 直接返回答案
```

### 2. 多轮迭代支持

- **最大轮数**: 3 轮 (`max_turns = 3`)
- **自动终止**: LLM 提供最终答案时自动停止
- **防止无限循环**: 达到最大轮数后返回提示信息

### 3. 详细的控制台日志

每次请求都会在服务器控制台输出详细的执行过程：

```
============================================================
[User] Who won the Super Bowl in 2025?
============================================================

[Turn 1/3]
[Agent] Decided to call 1 tool(s)
[Agent] Calling tool: 'web_search'
[Agent] Arguments: {'query': 'Super Bowl 2025 winner'}
[System] Tool Output: {...}

[Turn 2/3]
[Agent] Final Answer: The Philadelphia Eagles...
============================================================
```

## 实现细节

### 对话历史管理

```python
messages = [
    {"role": "user", "content": "用户问题"},
    {"role": "assistant", "content": None, "tool_calls": [...]},
    {"role": "tool", "tool_call_id": "...", "content": "工具结果"},
    {"role": "assistant", "content": "最终答案"}
]
```

### 工具调用流程

1. **LLM 决策阶段**
   ```python
   response = client.chat.completions.create(
       model="gpt-5",
       messages=messages,
       tools=TOOLS,
       tool_choice="auto"
   )
   ```

2. **检测工具调用**
   ```python
   if message.tool_calls:
       # 执行工具
   else:
       # 返回最终答案
   ```

3. **执行工具**
   ```python
   for tool_call in message.tool_calls:
       function_name = tool_call.function.name
       function_args = json.loads(tool_call.function.arguments)
       
       if function_name == "web_search":
           tool_result = web_search(query)
           messages.append({
               "role": "tool",
               "tool_call_id": tool_call.id,
               "content": json.dumps(tool_result)
           })
   ```

4. **继续循环**
   - 将工具结果添加到对话历史
   - 进入下一轮，让 LLM 处理结果
   - LLM 可以选择再次调用工具或提供最终答案

## 日志格式

### 用户输入
```
============================================================
[User] <用户问题>
============================================================
```

### 每轮开始
```
[Turn X/3]
```

### 工具调用决策
```
[Agent] Decided to call N tool(s)
[Agent] Calling tool: 'function_name'
[Agent] Arguments: {参数}
```

### 工具输出
```
[System] Tool Output: {结果}
```

### 最终答案
```
[Agent] Final Answer: <答案内容>
============================================================
```

### 错误处理
```
[System] Error: <错误信息>
```

## 测试结果

### ✅ 测试 1: 需要搜索的问题

**输入**: "Who won the Super Bowl in 2025?"

**执行过程**:
```
Turn 1/3: LLM 决定调用 web_search
          执行搜索: "Super Bowl 2025 winner"
          返回搜索结果

Turn 2/3: LLM 处理结果
          生成最终答案: "The Philadelphia Eagles..."
```

**输出**:
- Content: "The Philadelphia Eagles. They won Super Bowl LIX in 2025..."
- Tool Calls: 1 次 web_search
- 响应时间: ~16s

### ✅ 测试 2: 简单计算

**输入**: "What is 15 * 8?"

**执行过程**:
```
Turn 1/3: LLM 直接计算
          无需工具
          返回答案: "120"
```

**输出**:
- Content: "120"
- Tool Calls: null
- 响应时间: ~1.6s

### ✅ 测试 3: 当前信息查询

**输入**: "Who is the current president of the United States?"

**执行过程**:
```
Turn 1/3: LLM 决定调用 web_search
          执行搜索: "current president of the United States 2025"
          返回搜索结果

Turn 2/3: LLM 处理结果
          生成最终答案: "Donald J. Trump"
```

**输出**:
- Content: "As of December 2025, the president is Donald J. Trump."
- Tool Calls: 1 次 web_search
- 响应时间: ~21s

### ✅ 测试 4: 通用知识

**输入**: "What is the capital of France?"

**执行过程**:
```
Turn 1/3: LLM 直接回答
          无需工具
          返回答案: "Paris."
```

**输出**:
- Content: "Paris."
- Tool Calls: null
- 响应时间: ~1.6s

## 高级特性

### 1. 多工具调用支持

LLM 可以在一轮中调用多个工具：

```python
[Turn 1/3]
[Agent] Decided to call 3 tool(s)
[Agent] Calling tool: 'web_search'
[Agent] Arguments: {'query': 'Tokyo weather now'}
[Agent] Calling tool: 'web_search'
[Agent] Arguments: {'query': 'RJTT METAR now'}
[Agent] Calling tool: 'web_search'
[Agent] Arguments: {'query': 'JMA Tokyo weather'}
```

### 2. 错误处理

如果工具执行失败，错误信息会返回给 LLM：

```python
try:
    tool_result = web_search(query)
except Exception as e:
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps({"error": str(e)})
    })
```

### 3. 最大轮数保护

防止无限循环：

```python
if turn >= max_turns:
    return ChatResponse(
        content="I've reached the maximum number of steps...",
        tool_calls=all_tool_calls
    )
```

## API 响应格式

### 成功响应（有工具调用）

```json
{
  "content": "The Philadelphia Eagles. They won Super Bowl LIX...",
  "tool_calls": [
    {
      "id": "call_xxx",
      "function": "web_search",
      "arguments": {
        "query": "Super Bowl 2025 winner"
      }
    }
  ]
}
```

### 成功响应（无工具调用）

```json
{
  "content": "120",
  "tool_calls": null
}
```

### 错误响应

```json
{
  "detail": "Error in agentic loop: ..."
}
```

## 性能指标

| 场景 | 工具调用次数 | 平均响应时间 |
|------|-------------|-------------|
| 简单问题（无工具） | 0 | ~1.6s |
| 单次搜索 | 1 | ~16-21s |
| 多次搜索 | 2-3 | ~30-45s |

## 使用方法

### 通过 API

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Who won the Super Bowl in 2025?"}'
```

### 通过测试脚本

```bash
python3 test_agentic_loop.py
```

### 查看详细日志

服务器控制台会实时显示每一步的执行过程：

```bash
# 查看服务器日志
tail -f ~/.cursor/projects/Users-aiden-fastapiapp/terminals/12.txt
```

## 配置选项

### 修改最大轮数

在 `main.py` 中修改：

```python
max_turns = 3  # 改为你想要的值
```

### 添加新工具

1. 定义工具函数
2. 添加到 `TOOLS` schema
3. 在工具执行部分添加处理逻辑

```python
if function_name == "your_new_tool":
    result = your_new_tool(**function_args)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result)
    })
```

## 优势

1. **自主决策**: LLM 自动判断何时需要工具
2. **迭代处理**: 可以多次调用工具处理复杂查询
3. **透明可见**: 详细日志显示每一步决策
4. **错误恢复**: 工具失败时 LLM 可以尝试其他方法
5. **灵活扩展**: 易于添加新工具

## 限制

1. **最大轮数**: 限制为 3 轮防止无限循环
2. **同步执行**: 工具按顺序执行（未来可改为并行）
3. **单一模型**: 当前使用 gpt-5（可配置）
4. **搜索质量**: 依赖于搜索 API 返回的结果质量

## 下一步改进

1. **并行工具执行**: 同时执行多个独立的工具调用
2. **工具结果缓存**: 避免重复搜索相同内容
3. **流式响应**: 实时显示 LLM 的思考过程
4. **工具选择优化**: 让 LLM 更智能地选择工具
5. **对话历史持久化**: 支持多轮对话会话

## 总结

完整的 Agentic Loop 已成功实现，包括：

✅ 工具调用决策  
✅ 工具执行  
✅ 结果处理  
✅ 多轮迭代  
✅ 详细日志  
✅ 错误处理  
✅ 最大轮数保护  

系统现在可以自主地使用工具来回答需要实时信息的问题！

