# 调试指南 - Message History 打印

## 概述

已添加完整的消息历史打印功能，用于调试和检查 Agentic Loop 的执行过程。每次请求完成后，服务器控制台会打印完整的对话历史。

## 功能说明

### 自动打印时机

消息历史会在以下情况自动打印到控制台：

1. **正常完成**: LLM 提供最终答案时
2. **达到最大轮数**: 超过 5 轮迭代时

### 打印格式

```
================================================================================
📋 COMPLETE MESSAGE HISTORY (DEBUG)
================================================================================

[Message 1] Role: USER
--------------------------------------------------------------------------------
Content: <用户问题>

[Message 2] Role: ASSISTANT
--------------------------------------------------------------------------------
Content: None
Tool Calls: 2 call(s)
  [1] Function: web_search
      ID: call_xxx
      Arguments: {"query":"..."}
  [2] Function: read_page
      ID: call_yyy
      Arguments: {"url":"..."}

[Message 3] Role: TOOL
--------------------------------------------------------------------------------
Tool Call ID: call_xxx
Result Type: web_search
  Number of queries: 1
  First query keyword: ...

[Message 4] Role: TOOL
--------------------------------------------------------------------------------
Tool Call ID: call_yyy
Result Type: read_page
  URL: https://example.com
  Title: Page Title
  Content Length: 8038 chars
  Content Preview: ...

[Message 5] Role: ASSISTANT
--------------------------------------------------------------------------------
Content: <最终答案>

================================================================================
📋 END OF MESSAGE HISTORY
================================================================================
```

## 消息类型详解

### 1. USER 消息

显示用户的原始问题：

```
[Message 1] Role: USER
--------------------------------------------------------------------------------
Content: Who won the Super Bowl in 2025?
```

### 2. ASSISTANT 消息（带工具调用）

当 LLM 决定调用工具时：

```
[Message 2] Role: ASSISTANT
--------------------------------------------------------------------------------
Content: None

Tool Calls: 2 call(s)
  [1] Function: web_search
      ID: call_GYryUfuDlAcrubdhZ42bx2Gh
      Arguments: {"query":"Super Bowl 2025 winner"}
  [2] Function: read_page
      ID: call_u43jQO895KYet4SiuwPCDDQd
      Arguments: {"url":"https://example.com"}
```

**关键信息：**
- `Content: None` - 调用工具时通常没有文本内容
- `Tool Calls` - 列出所有工具调用
- `ID` - 工具调用的唯一标识符
- `Arguments` - 传递给工具的参数（JSON 格式）

### 3. TOOL 消息（web_search 结果）

搜索工具的返回结果：

```
[Message 3] Role: TOOL
--------------------------------------------------------------------------------
Tool Call ID: call_GYryUfuDlAcrubdhZ42bx2Gh
Result Type: web_search
  Number of queries: 1
  First query keyword: Super Bowl 2025 winner
```

### 4. TOOL 消息（read_page 结果）

页面读取工具的返回结果：

```
[Message 4] Role: TOOL
--------------------------------------------------------------------------------
Tool Call ID: call_u43jQO895KYet4SiuwPCDDQd
Result Type: read_page
  URL: https://www.nfl.com/news/...
  Title: Chiefs-Eagles in Super Bowl LIX
  Content Length: 8038 chars
  Content Preview: Chiefs-Eagles in Super Bowl LIX: What We Learned...
```

### 5. TOOL 消息（错误）

当工具执行失败时：

```
[Message 5] Role: TOOL
--------------------------------------------------------------------------------
Tool Call ID: call_xxx
Result: ERROR - Failed to fetch page: 403 Client Error: Forbidden
```

### 6. ASSISTANT 消息（最终答案）

LLM 处理所有工具结果后的最终回答：

```
[Message 6] Role: ASSISTANT
--------------------------------------------------------------------------------
Content: The Philadelphia Eagles. They won Super Bowl LIX in 2025, 
defeating the Kansas City Chiefs 40–22.
```

## 实际示例

### 示例 1: 简单问题（无工具）

**请求:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "What is 50 + 50?"}'
```

**消息历史:**
```
[Message 1] Role: USER
Content: What is 50 + 50?

[Message 2] Role: ASSISTANT
Content: 100
```

**分析:** 只有 2 条消息，LLM 直接回答，无需工具。

### 示例 2: 使用 web_search

**请求:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Who won the Super Bowl in 2025?"}'
```

**消息历史:**
```
[Message 1] Role: USER
Content: Who won the Super Bowl in 2025?

[Message 2] Role: ASSISTANT
Content: None
Tool Calls: 1 call(s)
  [1] Function: web_search
      Arguments: {"query":"Super Bowl 2025 winner"}

[Message 3] Role: TOOL
Tool Call ID: call_xxx
Result Type: web_search
  Number of queries: 1

[Message 4] Role: ASSISTANT
Content: None
Tool Calls: 1 call(s)
  [1] Function: read_page
      Arguments: {"url":"https://www.nfl.com/..."}

[Message 5] Role: TOOL
Tool Call ID: call_yyy
Result Type: read_page
  URL: https://www.nfl.com/...
  Content Length: 8038 chars

[Message 6] Role: ASSISTANT
Content: The Philadelphia Eagles. They won...
```

**分析:** 6 条消息，展示了完整的工具调用链：
1. 用户问题
2. LLM 决定搜索
3. 搜索结果
4. LLM 决定读取页面
5. 页面内容
6. 最终答案

### 示例 3: 多工具并行调用

**请求:**
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "What are the top crypto news headlines?"}'
```

**消息历史片段:**
```
[Message 2] Role: ASSISTANT
Tool Calls: 8 call(s)
  [1] Function: web_search
      Arguments: {"query":"CoinDesk top stories"}
  [2] Function: web_search
      Arguments: {"query":"Cointelegraph latest"}
  [3] Function: web_search
      Arguments: {"query":"The Block crypto"}
  ... (5 more searches)

[Message 3-10] Role: TOOL
(8 个搜索结果)

[Message 11] Role: ASSISTANT
Tool Calls: 5 call(s)
  [1] Function: read_page
      Arguments: {"url":"https://www.cnbc.com/crypto/"}
  [2] Function: read_page
      Arguments: {"url":"https://decrypt.co/news"}
  ... (3 more read_page calls)
```

**分析:** 展示了 LLM 如何：
1. 并行调用多个搜索
2. 基于搜索结果选择页面阅读
3. 综合所有信息生成答案

## 调试技巧

### 1. 检查工具调用决策

查看 `ASSISTANT` 消息的 `Tool Calls` 部分：
- LLM 选择了哪些工具？
- 参数是否合理？
- 是否有不必要的重复调用？

### 2. 检查工具结果

查看 `TOOL` 消息：
- 工具是否成功执行？
- 返回的数据是否有用？
- 是否有错误？

### 3. 追踪信息流

按顺序阅读消息：
1. 用户问题 → 
2. LLM 决策（工具调用）→ 
3. 工具结果 → 
4. LLM 再次决策 → 
5. ... → 
6. 最终答案

### 4. 识别问题

**常见问题模式：**

**问题 1: 空内容**
```
[Message N] Role: ASSISTANT
Content: None
```
如果这是最后一条消息，说明 LLM 没有生成答案。

**问题 2: 工具失败**
```
[Message N] Role: TOOL
Result: ERROR - ...
```
工具执行失败，检查 URL 或查询参数。

**问题 3: 信息过载**
```
[Message 2] Role: ASSISTANT
Tool Calls: 15 call(s)
```
太多工具调用可能导致上下文溢出。

## 查看日志

### 实时查看
```bash
tail -f ~/.cursor/projects/Users-aiden-fastapiapp/terminals/3.txt
```

### 查看最近的消息历史
```bash
tail -200 ~/.cursor/projects/Users-aiden-fastapiapp/terminals/3.txt | \
  grep -A 200 "COMPLETE MESSAGE HISTORY"
```

### 搜索特定请求
```bash
grep -A 100 "Who won the Super Bowl" \
  ~/.cursor/projects/Users-aiden-fastapiapp/terminals/3.txt
```

## 性能影响

- **打印开销**: 最小，仅在请求完成后打印
- **日志大小**: 每个请求约 1-5KB（取决于工具调用数量）
- **不影响**: API 响应时间或功能

## 禁用调试输出

如果需要禁用消息历史打印，注释掉以下行：

```python
# main.py 中的两处调用
# print_message_history(messages)
```

## 总结

消息历史打印功能提供了：

✅ **完整可见性** - 看到每一步的决策和结果  
✅ **易于调试** - 快速定位问题  
✅ **学习工具** - 理解 LLM 如何使用工具  
✅ **性能分析** - 识别瓶颈和优化机会  

这是调试和优化 Agentic Loop 的强大工具！🔍

