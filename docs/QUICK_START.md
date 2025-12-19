# 快速开始指南

## 🚀 5 分钟快速启动

### 1. 确保已设置 API 密钥

```bash
# 检查 .env 文件是否存在
ls -la .env

# 如果不存在，创建它
echo "SUPER_MIND_API_KEY=your_api_key_here" > .env
```

### 2. 启动服务器

```bash
./start_server.sh
```

看到这个输出表示成功：
```
✅ Loaded environment variables from .env file
🚀 Starting FastAPI server...
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. 测试 API

**方法 1: 使用测试脚本**
```bash
python3 test_tool_calling.py
```

**方法 2: 使用 curl**
```bash
# 简单问题
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "What is 2 + 2?"}'

# 需要搜索的问题
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "Who won the Super Bowl?"}'
```

**方法 3: 使用浏览器**
访问 http://127.0.0.1:8000/docs

## 📚 核心概念

### 工具调用是什么？

当你问 LLM 一个需要实时信息的问题时，它会自动决定调用 `web_search` 工具。

**示例：**

❓ **问题**: "Who won the Super Bowl?"

🤖 **LLM 的决策**: "这需要最新信息，我应该搜索"

🔧 **工具调用**:
```json
{
  "function": "web_search",
  "arguments": {
    "query": "Super Bowl LIX winner"
  }
}
```

### 何时会调用工具？

✅ **会调用工具：**
- "Who won the Super Bowl?" (最新赛事)
- "What's the weather in Tokyo?" (实时信息)
- "Who is the current CEO of Apple?" (可能变化的信息)

❌ **不会调用工具：**
- "What is 2 + 2?" (数学计算)
- "Explain Python" (通用知识)
- "Who was Albert Einstein?" (历史事实)

## 🎯 常用命令

```bash
# 启动服务器
./start_server.sh

# 停止服务器
pkill -f "uvicorn main:app"

# 查看服务器日志
tail -f ~/.cursor/projects/Users-aiden-fastapiapp/terminals/*.txt

# 运行测试
python3 test_tool_calling.py

# 查看 API 文档
open http://127.0.0.1:8000/docs
```

## 📁 重要文件

| 文件 | 用途 |
|------|------|
| `main.py` | 主应用代码 |
| `start_server.sh` | 启动脚本 |
| `test_tool_calling.py` | 测试脚本 |
| `.env` | API 密钥配置 |
| `TOOL_CALLING.md` | 详细文档 |

## 🔍 调试技巧

### 检查服务器是否运行
```bash
curl http://127.0.0.1:8000/
# 应该返回: {"message":"Chat API is running..."}
```

### 检查 API 密钥是否加载
查看服务器启动日志，应该看到：
```
✅ Loaded environment variables from .env file
```

### 查看详细响应
```bash
curl -s -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_message": "test"}' | python3 -m json.tool
```

## 💡 提示

1. **自动重载**: 修改 `main.py` 后服务器会自动重启
2. **API 文档**: 访问 `/docs` 可以交互式测试 API
3. **日志查看**: 服务器输出会保存在 terminals 文件夹
4. **端口占用**: 如果 8000 端口被占用，先停止旧进程

## 📖 更多信息

- 详细文档: `TOOL_CALLING.md`
- 项目总结: `SUMMARY.md`
- 完整说明: `README.md`

## 🆘 常见问题

**Q: 服务器启动失败？**
A: 检查 `.env` 文件是否存在，API 密钥是否正确

**Q: 工具调用不工作？**
A: 确保使用的是需要实时信息的问题

**Q: 端口被占用？**
A: 运行 `pkill -f "uvicorn main:app"` 停止旧进程

**Q: 权限错误？**
A: 使用 `./start_server.sh` 而不是直接运行 `uvicorn`

