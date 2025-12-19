# Focus Catcher 🎯

> 零打断的学习助手 - 快速捕捉、智能分组、AI 回顾

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green.svg)](https://developer.chrome.com/docs/extensions/)

---

## 📖 项目简介

Focus Catcher 是一个专为学习场景设计的内容捕捉与回顾工具。它让你在阅读网页时，可以快速捕捉重要内容，系统会自动按主题分组，并使用 AI 生成学习回顾，充当你的"记忆锚点"。

### 核心特点

- 🚀 **零打断捕捉**：右键菜单，一键捕捉选中文字
- 🤖 **智能主题分组**：AI 自动识别主题切换，无需手动管理
- 📚 **AI 学习回顾**：自动生成核心要点、知识脉络、回顾建议
- 💾 **本地存储**：数据存储在本地，隐私安全
- ⚡ **响应迅速**：捕捉响应时间 < 100ms

---

## 🎬 快速开始

### 前置要求

- Python 3.8+
- Chrome 浏览器
- Google Gemini API Key（免费）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/focus-catcher.git
cd focus-catcher
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API Key：

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> 💡 如何获取 Google Gemini API Key：访问 [Google AI Studio](https://makersuite.google.com/app/apikey)

#### 4. 启动后端服务

```bash
./start.sh
```

访问 `http://localhost:8000/api` 确认服务运行正常。

#### 5. 安装 Chrome 插件

1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 开启右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `chrome-extension` 目录
6. 完成！

---

## 🎯 使用方法

### 方式 1：右键菜单（推荐 ⭐）

1. 在任意网页选中文字
2. 右键点击选中的文字
3. 选择 **"🎯 Focus Catcher - 捕捉选中内容"**
4. 看到 "✅ 已捕捉" 提示即成功

### 方式 2：快捷键

1. 访问 `chrome://extensions/shortcuts`
2. 为 "Focus Catcher" 设置快捷键（如 `Cmd+1`）
3. 选中文字后按快捷键

### 查看捕捉历史

访问 `http://localhost:8000/test_capture.html`

- 查看所有捕捉记录（按会话分组）
- 对会话进行 AI 分析（>= 5 条捕捉）
- 删除不需要的会话

---

## 🏗️ 项目架构

```
focus-catcher/
├── main.py                 # FastAPI 后端主文件
├── database.py             # 数据库模型
├── focus_prompts.py        # AI 分析 prompts
├── requirements.txt        # Python 依赖
├── start.sh               # 启动脚本
│
├── chrome-extension/       # Chrome 插件
│   ├── manifest.json      # 插件配置
│   ├── background.js      # 后台脚本
│   ├── content.js         # 内容脚本
│   ├── popup.html         # 弹出页面
│   ├── settings.html      # 设置页面
│   └── icons/             # 插件图标
│
├── frontend/              # 前端页面
│   └── test_capture.html # 历史记录页面
│
└── docs/                  # 文档
    ├── PRODUCT_STORY.md   # 产品故事
    ├── QUICK_START.md     # 快速开始
    └── ...
```

---

## 🤖 智能主题检测

Focus Catcher 使用 AI 来判断你是否切换了学习主题，而不是简单地使用时间来分割会话。

### 工作原理

1. 捕捉新内容时，获取最近 3 条捕捉
2. 使用 Gemini AI 比较新旧内容
3. 判断主题是否相关：
   - ✅ 相关 → 继续当前会话
   - ❌ 不相关 → 创建新会话

### 判断标准

**相关（继续当前会话）**：
- 同一技术栈（如都是 React）
- 同一问题领域（如都是数据库优化）
- 相关概念（如 JavaScript → TypeScript）

**不相关（创建新会话）**：
- 完全不同的领域（React → Python）
- 不同的技术（前端 → 后端）
- 不同的话题（编程 → 设计）

---

## 📊 AI 分析功能

当一个会话积累了 5 条以上的捕捉后，可以进行 AI 分析。

### 分析维度

- 🎯 **核心主题**：你在学什么？
- 📚 **关键信息点**：重点是什么？
- 🔗 **内容脉络**：知识如何关联？
- ✅ **已覆盖的内容**：你已经掌握了什么？
- ❓ **可能需要进一步查阅**：还有哪些疑问？
- 💡 **回顾建议**：下一步怎么做？
- 📝 **原文回顾**：完整的捕捉内容

### 输出格式

纯文本格式，易于阅读和复制，可以直接粘贴到笔记软件。

---

## ⚙️ 配置选项

### 插件设置

点击插件图标 → "⚙️ 设置"，可以配置：

- **捕捉行为**
  - 双击自动捕捉
  - 显示 Toast 提示
  - 播放提示音

- **AI 分析**
  - 自动触发 AI 分析
  - 自定义分析阈值（3-20 条）

---

## 📚 文档

- [产品故事](PRODUCT_STORY.md) - 从想法到实现的完整过程
- [快速开始](chrome-extension/QUICK_START.md) - 5 分钟上手指南
- [设置指南](chrome-extension/SETTINGS_GUIDE.md) - 详细的设置说明
- [故障排除](chrome-extension/TROUBLESHOOTING.md) - 常见问题解决方案
- [更新日志](chrome-extension/CHANGELOG.md) - 版本更新记录

---

## 🛠️ 技术栈

### 后端
- **FastAPI** - 轻量级 Web 框架
- **SQLAlchemy** - ORM 框架
- **SQLite** - 本地数据库
- **Google Gemini** - AI 分析引擎

### 前端
- **Chrome Extension Manifest V3** - 插件框架
- **Vanilla JavaScript** - 无框架依赖
- **CSS3** - 现代样式

---

## 🚀 性能指标

- **捕捉响应时间**：< 100ms
- **AI 主题检测**：< 1s
- **AI 分析生成**：3-5s（取决于捕捉数量）
- **内存占用**：< 50MB（插件）
- **数据库大小**：< 10MB（1000 条捕捉）

---

## 🗺️ 路线图

### v1.0（当前版本）
- ✅ 右键菜单捕捉
- ✅ 智能主题检测
- ✅ AI 学习回顾
- ✅ 会话管理
- ✅ 设置页面

### v1.1（计划中）
- [ ] 插件内查看历史记录
- [ ] 导出学习报告
- [ ] 支持图片捕捉
- [ ] 添加标签系统

### v2.0（远期规划）
- [ ] 跨设备同步
- [ ] 移动端支持
- [ ] 知识图谱可视化
- [ ] 团队协作功能

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 启动开发服务器
./start.sh
```

---

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🙏 致谢

- 灵感来源于课代表和鸭哥新课的 "Aha! Catcher"
- 感谢 [Cursor](https://cursor.sh/) 和 [Claude](https://www.anthropic.com/) 提供的 AI 辅助开发
- 感谢 [Google Gemini](https://ai.google.dev/) 提供的强大 AI 能力
- 感谢所有测试用户的反馈

---

## 📧 联系方式

- 项目主页：[GitHub](https://github.com/yourusername/focus-catcher)
- 问题反馈：[Issues](https://github.com/yourusername/focus-catcher/issues)
- 邮件：your.email@example.com

---

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star ⭐！

---

**Made with ❤️ by Focus Catcher Team**

*最后更新：2024-12-19*
