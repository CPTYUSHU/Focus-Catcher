# read_page 工具文档

## 概述

已成功添加第二个工具 `read_page(url: str)`，它可以获取网页内容并提取主要文本，与 `web_search` 工具配合使用，形成完整的信息检索系统。

## 功能特性

### 1. 网页内容提取

```python
def read_page(url: str) -> dict:
    """
    获取网页并提取主要文本内容
    
    Args:
        url: 要读取的页面 URL
        
    Returns:
        dict: 包含 URL、标题和提取的文本内容
    """
```

### 2. 智能文本清理

- ✅ 移除 `<script>` 和 `<style>` 标签
- ✅ 移除导航、页脚、页眉元素
- ✅ 清理多余空白和换行
- ✅ 限制内容长度（最多 8000 字符）

### 3. 返回格式

```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "content": "Extracted text content...",
  "length": 2174
}
```

## 工具定义

### Schema

```python
{
    "type": "function",
    "function": {
        "name": "read_page",
        "description": "Fetch and read the content of a specific web page. Use this when you have a URL and need to extract detailed information from that page.",
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
```

## 使用场景

### 1. 与 web_search 配合

**工作流程**:
1. 使用 `web_search` 找到相关页面
2. 使用 `read_page` 读取具体页面内容
3. LLM 基于页面内容生成答案

**示例**:
```
User: "Search for the latest Python release and tell me about new features"

Turn 1: web_search("latest Python release")
        → 找到 Python 3.14 发布信息
        
Turn 2: read_page("https://docs.python.org/3/whatsnew/3.14.html")
        → 读取详细的 changelog
        
Turn 3: 生成基于实际内容的答案
```

### 2. 直接读取已知 URL

**示例**:
```
User: "What is on the Python homepage?"

Turn 1: read_page("https://www.python.org/")
        → 提取主页内容
        
Turn 2: 生成内容摘要
```

## 测试结果

### ✅ 测试 1: Super Bowl 查询（自动使用两个工具）

**输入**: "Who won the Super Bowl in 2025?"

**执行过程**:
```
Turn 1: web_search("Super Bowl 2025 winner")
        → 找到相关新闻链接

Turn 2: read_page("https://www.npr.org/2025/02/09/...")
        → 读取新闻文章详细内容

Turn 3: 生成答案
```

**输出**: "The Philadelphia Eagles. They won Super Bowl LIX in 2025, beating the Kansas City Chiefs 40–22."

**工具调用**: 2 次（web_search + read_page）  
**响应时间**: ~19.7s

### ✅ 测试 2: Python 主页查询

**输入**: "What is on the Python homepage at python.org?"

**执行过程**:
```
Turn 1: read_page("https://www.python.org/")
        → 提取主页内容（2174 字符）

Turn 2: 生成详细摘要
```

**输出**: 详细的主页内容摘要，包括：
- 最新发布版本
- 新闻更新
- 即将举行的活动
- 成功案例
- 常用库和框架

**工具调用**: 1 次（read_page）  
**响应时间**: ~30s

### ✅ 测试 3: 简单查询（不需要工具）

**输入**: "Search for Python official website and tell me the URL"

**执行过程**:
```
Turn 1: 直接回答（LLM 已知信息）
```

**输出**: "https://www.python.org/"

**工具调用**: 0 次  
**响应时间**: ~11.8s

## 日志示例

### read_page 工具调用日志

```
[Turn 1/5]
[Agent] Decided to call 1 tool(s)
[Agent] Calling tool: 'read_page'
[Agent] Arguments: {'url': 'https://www.python.org/'}
[System] Tool Output (read_page):
[System]   URL: https://www.python.org/
[System]   Title: Welcome to Python.org
[System]   Content length: 2174 characters
[System]   Preview: Welcome to Python.org
Notice:
While JavaScript is not essential...

[Turn 2/5]
[Agent] Final Answer: Here's a concise snapshot of what's on...
```

## 技术实现

### 依赖库

```python
from bs4 import BeautifulSoup  # HTML 解析
import requests                # HTTP 请求
```

### 核心逻辑

```python
# 1. 获取页面
response = requests.get(url, headers=headers, timeout=10)

# 2. 解析 HTML
soup = BeautifulSoup(response.content, 'lxml')

# 3. 移除不需要的元素
for script in soup(["script", "style", "nav", "footer", "header"]):
    script.decompose()

# 4. 提取文本
text = soup.get_text(separator='\n', strip=True)

# 5. 清理空白
lines = (line.strip() for line in text.splitlines())
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
text = '\n'.join(chunk for chunk in chunks if chunk)

# 6. 限制长度
if len(text) > 8000:
    text = text[:8000] + "\n\n[Content truncated...]"
```

## 工具对比

| 特性 | web_search | read_page |
|------|-----------|-----------|
| 用途 | 搜索相关信息 | 读取具体页面 |
| 输入 | 搜索查询 | URL |
| 输出 | 搜索结果列表 | 页面文本内容 |
| 适用场景 | 不知道具体 URL | 已知 URL |
| 返回内容 | 摘要和链接 | 完整文本 |

## 最佳实践

### 1. 工具选择

- **使用 web_search**: 当你需要找到相关信息但不知道具体 URL
- **使用 read_page**: 当你有具体 URL 需要读取详细内容
- **组合使用**: 先搜索找到 URL，再读取页面获取详细信息

### 2. 性能考虑

- `read_page` 会下载完整页面，比 `web_search` 慢
- 内容限制在 8000 字符以避免超出 LLM 上下文
- 设置 10 秒超时防止长时间等待

### 3. 错误处理

```python
try:
    result = read_page(url)
except Exception as e:
    # 错误信息会返回给 LLM
    # LLM 可以尝试其他方法或告知用户
```

## 配置选项

### 修改内容长度限制

在 `main.py` 中修改：

```python
max_length = 8000  # 改为你想要的值
```

### 修改超时时间

```python
response = requests.get(url, headers=headers, timeout=10)  # 改为你想要的秒数
```

### 自定义元素移除

```python
# 添加更多要移除的标签
for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
    element.decompose()
```

## 限制和注意事项

1. **JavaScript 渲染**: 不支持需要 JavaScript 渲染的动态内容
2. **内容长度**: 限制在 8000 字符，超长内容会被截断
3. **访问限制**: 某些网站可能阻止爬虫访问
4. **性能**: 每次调用需要下载完整页面，较慢

## 未来改进

1. **JavaScript 支持**: 使用 Selenium 或 Playwright 支持动态内容
2. **智能摘要**: 自动提取最重要的内容
3. **缓存机制**: 缓存已读取的页面
4. **并行处理**: 同时读取多个页面
5. **格式保留**: 保留一些重要的格式信息（标题、列表等）

## 总结

`read_page` 工具成功添加并与 `web_search` 形成完整的信息检索系统：

✅ 网页内容提取  
✅ 智能文本清理  
✅ 与 web_search 配合  
✅ 详细日志输出  
✅ 错误处理  
✅ 性能优化（内容限制、超时）  

现在 LLM 可以：
1. 搜索信息 (web_search)
2. 读取页面 (read_page)
3. 基于实际内容生成答案

形成完整的 Agentic Loop！

