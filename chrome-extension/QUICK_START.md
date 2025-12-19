# Focus Catcher - 快速开始指南 🚀

## 5 分钟上手

### 步骤 1：启动后端服务（1 分钟）

```bash
cd /Users/aiden/fastapiapp
./start.sh
```

✅ 看到 "Uvicorn running on http://127.0.0.1:8000" 即成功

### 步骤 2：安装 Chrome 插件（2 分钟）

1. 打开 Chrome 浏览器
2. 地址栏输入：`chrome://extensions/`
3. 打开右上角的 **"开发者模式"**
4. 点击 **"加载已解压的扩展程序"**
5. 选择目录：`/Users/aiden/fastapiapp/chrome-extension`
6. 完成！

### 步骤 3：测试捕捉功能（2 分钟）

#### 方法 1：右键菜单（推荐 ⭐）

1. 打开任意网页（例如：Wikipedia、Medium、知乎）
2. 用鼠标选中一段文字
3. **右键点击** 选中的文字
4. 选择 **"🎯 Focus Catcher - 捕捉选中内容"**
5. 看到右上角 **"✅ 已捕捉"** 提示即成功！

#### 方法 2：快捷键（需要先设置）

1. 访问 `chrome://extensions/shortcuts`
2. 为 "Focus Catcher" 设置快捷键（如 `Cmd+1`）
3. 在任意网页选中文字
4. 按快捷键
5. 看到 **"✅ 已捕捉"** 提示即成功！

#### 方法 3：在测试页面验证

1. 打开：`http://localhost:8000/test_capture.html`
2. 在"快速捕捉"区域输入文字
3. 点击"捕捉"按钮
4. 查看下方的历史记录

### 步骤 4：查看 AI 分析

1. 捕捉 5 条以上内容
2. 在历史记录中点击 **"🤖 AI 分析"** 按钮
3. 等待 3-5 秒
4. 查看 AI 生成的学习回顾

---

## 常见问题

### Q1: 快捷键不工作？

**解决方案**：
1. 刷新页面后重试
2. 检查是否有其他插件占用了快捷键
3. 访问 `chrome://extensions/shortcuts` 自定义快捷键

### Q2: 显示 "❌ 捕捉失败"？

**解决方案**：
1. 确认后端服务正在运行
2. 访问 `http://localhost:8000/api` 应该看到 JSON 响应
3. 检查浏览器控制台（F12）是否有错误

### Q3: 没有看到 Toast 提示？

**解决方案**：
1. 确保已经选中了文字（文字应该高亮显示）
2. 打开浏览器控制台（F12）查看是否有错误
3. 尝试刷新页面后重试

---

## 调试技巧

### 查看 Content Script 日志

1. 打开任意网页
2. 按 `F12` 打开开发者工具
3. 切换到 **Console** 标签
4. 应该看到：`[Focus Catcher] Content script loaded`

### 查看 Background Script 日志

1. 访问 `chrome://extensions/`
2. 找到 **Focus Catcher**
3. 点击 **"检查视图：Service Worker"**
4. 查看 Console 日志

### 查看后端日志

在运行 `./start.sh` 的终端中查看实时日志：
- `[Focus Catcher] 🎯 New capture request...`
- `[Focus Catcher] ✅ Capture saved successfully`

---

## 下一步

- 🎯 在真实学习场景中使用（阅读技术文档、博客文章）
- 📊 积累 5-10 条捕捉后查看 AI 分析
- 🗑️ 删除不需要的会话
- 🔄 尝试不同主题的内容，体验自动分会话

---

**Enjoy! 🎉**

