# 贡献指南 🤝

感谢你对 Focus Catcher 的关注！我们欢迎任何形式的贡献。

## 如何贡献

### 报告 Bug 🐛

如果你发现了 Bug，请：

1. 检查 [Issues](https://github.com/yourusername/focus-catcher/issues) 是否已有相同问题
2. 如果没有，创建新 Issue，包含：
   - 清晰的标题
   - 详细的问题描述
   - 复现步骤
   - 预期行为 vs 实际行为
   - 环境信息（OS、浏览器版本、Python 版本）
   - 截图或日志（如果适用）

### 提出新功能 💡

如果你有好的想法：

1. 先创建一个 Issue 讨论
2. 说明功能的用途和价值
3. 等待维护者反馈
4. 获得认可后再开始开发

### 提交代码 🔧

#### 1. Fork 项目

点击右上角的 "Fork" 按钮

#### 2. 克隆到本地

```bash
git clone https://github.com/your-username/focus-catcher.git
cd focus-catcher
```

#### 3. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug 修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试相关

#### 4. 设置开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 添加你的 API Key

# 启动开发服务器
./start.sh
```

#### 5. 开发你的功能

- 遵循现有代码风格
- 添加必要的注释
- 更新相关文档
- 添加测试（如果适用）

#### 6. 测试你的更改

```bash
# 运行测试
pytest tests/

# 手动测试
# 1. 启动后端服务
./start.sh

# 2. 在 Chrome 中加载插件
# 3. 测试所有相关功能
```

#### 7. 提交更改

```bash
git add .
git commit -m "feat: add awesome feature"
```

提交信息格式：
- `feat: xxx` - 新功能
- `fix: xxx` - Bug 修复
- `docs: xxx` - 文档更新
- `style: xxx` - 代码格式（不影响功能）
- `refactor: xxx` - 代码重构
- `test: xxx` - 测试相关
- `chore: xxx` - 构建/工具相关

#### 8. 推送到你的 Fork

```bash
git push origin feature/your-feature-name
```

#### 9. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "New Pull Request"
3. 填写 PR 描述：
   - 做了什么改动
   - 为什么要做这个改动
   - 如何测试
   - 相关 Issue（如果有）
4. 等待 Review

## 代码规范

### Python 代码

- 使用 PEP 8 风格
- 函数和变量使用 snake_case
- 类名使用 PascalCase
- 添加类型注解（Type Hints）
- 添加 docstring

示例：

```python
def analyze_session(session_id: int, db: Session) -> dict:
    """
    Analyze a learning session using AI.
    
    Args:
        session_id: The ID of the session to analyze
        db: Database session
        
    Returns:
        dict: Analysis results including core_goal, main_thread, etc.
        
    Raises:
        HTTPException: If session not found or analysis fails
    """
    # Implementation
    pass
```

### JavaScript 代码

- 使用 ES6+ 语法
- 使用 camelCase 命名
- 添加 JSDoc 注释
- 使用 `const` 和 `let`，避免 `var`

示例：

```javascript
/**
 * Send captured text to backend API
 * @param {string} selectedText - The text to capture
 * @param {string} pageUrl - Current page URL
 * @param {string} pageTitle - Current page title
 * @returns {Promise<Object>} API response
 */
async function sendToBackend(selectedText, pageUrl, pageTitle) {
    // Implementation
}
```

### 文档

- 使用 Markdown 格式
- 保持简洁清晰
- 添加代码示例
- 更新目录（如果需要）

## 项目结构

```
focus-catcher/
├── main.py              # FastAPI 后端主文件
├── database.py          # 数据库模型
├── focus_prompts.py     # AI prompts
├── chrome-extension/    # Chrome 插件
├── frontend/           # 前端页面
├── docs/               # 文档
├── tests/              # 测试
└── scripts/            # 脚本
```

## 开发流程

### 添加新功能

1. 在 `main.py` 中添加 API 端点
2. 更新 `database.py`（如果需要新表）
3. 更新 Chrome 插件（如果需要）
4. 更新前端页面（如果需要）
5. 添加测试
6. 更新文档

### 修复 Bug

1. 定位问题代码
2. 编写测试用例复现 Bug
3. 修复代码
4. 确保测试通过
5. 更新相关文档

## 测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_agentic_loop.py

# 查看覆盖率
pytest --cov=. tests/
```

### 手动测试清单

- [ ] 捕捉功能正常
- [ ] 主题检测准确
- [ ] AI 分析生成正确
- [ ] 会话管理功能正常
- [ ] 设置页面功能正常
- [ ] 在不同网站测试
- [ ] 测试边界情况

## 发布流程

（仅维护者）

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git tag
4. 推送到 GitHub
5. 创建 Release
6. 发布到 Chrome Web Store（如果适用）

## 社区

- GitHub Issues: 报告问题和讨论
- Pull Requests: 代码贡献
- Discussions: 功能讨论和交流

## 行为准则

- 尊重所有贡献者
- 保持友好和专业
- 接受建设性批评
- 关注项目的最佳利益

## 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。

## 问题？

如有任何问题，请：
- 创建 Issue
- 发送邮件到 your.email@example.com

---

再次感谢你的贡献！🎉

