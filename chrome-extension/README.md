# Focus Catcher - Chrome 插件

快速捕捉学习内容，零打断的学习助手 🎯

## 功能特点

- ✅ **快捷键捕捉**：选中文字后按 `Cmd+Shift+C`（Mac）或 `Ctrl+Shift+C`（Windows）
- ✅ **任意网页可用**：在任何网站都能使用
- ✅ **零打断体验**：捕捉后立即显示提示，不影响阅读
- ✅ **智能分组**：自动根据主题创建学习会话
- ✅ **AI 分析**：积累 5-10 条后可进行 AI 分析

## 安装步骤

### 1. 确保后端服务运行

```bash
cd /Users/aiden/fastapiapp
./start.sh
```

确保 FastAPI 服务在 `http://localhost:8000` 运行。

### 2. 加载 Chrome 插件

1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 打开右上角的"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `/Users/aiden/fastapiapp/chrome-extension` 目录
6. 完成！🎉

## 使用方法

### 方式 1：右键菜单（推荐 ⭐）

1. 在任意网页选中文字
2. 右键点击选中的文字
3. 选择 **"🎯 Focus Catcher - 捕捉选中内容"**
4. 看到 "✅ 已捕捉" 提示即成功

### 方式 2：快捷键

1. 在任意网页选中文字
2. 按快捷键（需要在 `chrome://extensions/shortcuts` 设置）
3. 推荐设置：`Cmd+1`（Mac）或 `Ctrl+1`（Windows）
4. 看到 "✅ 已捕捉" 提示即成功

### 方式 3：插件图标

1. 点击浏览器工具栏的 Focus Catcher 图标
2. 查看今日统计
3. 点击"查看历史记录"打开管理页面

## 查看捕捉历史

访问：`http://localhost:8000/test_capture.html`

在这里你可以：
- 查看所有捕捉记录（按会话分组）
- 对会话进行 AI 分析（>= 5 条捕捉）
- 删除不需要的会话

## 快捷键自定义

1. 访问 `chrome://extensions/shortcuts`
2. 找到 "Focus Catcher"
3. 自定义你喜欢的快捷键

## 文件结构

```
chrome-extension/
├── manifest.json       # 插件配置
├── content.js          # 内容脚本（监听选中 + 快捷键）
├── content.css         # Toast 样式
├── background.js       # 后台脚本（与 FastAPI 通信）
├── popup.html          # 弹出页面
├── popup.js            # 弹出页面脚本
├── icons/              # 插件图标
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md           # 本文件
```

## 故障排除

### 问题 1：快捷键不工作

**解决方案**：
1. 检查快捷键是否被其他插件占用
2. 访问 `chrome://extensions/shortcuts` 重新设置
3. 刷新页面后重试

### 问题 2：捕捉失败（❌ 捕捉失败）

**解决方案**：
1. 确认 FastAPI 服务正在运行（`http://localhost:8000/api` 应返回 JSON）
2. 检查浏览器控制台是否有 CORS 错误
3. 确认插件有 `http://localhost:8000/*` 的权限

### 问题 3：没有选中文字提示

**解决方案**：
- 确保在按快捷键前已经选中了文字
- 文字选中状态应该是高亮显示的

## 开发说明

### 修改后重新加载

1. 修改代码后
2. 访问 `chrome://extensions/`
3. 点击 Focus Catcher 的"刷新"按钮
4. 刷新测试页面

### 查看日志

- **Content Script 日志**：打开网页的开发者工具（F12）→ Console
- **Background Script 日志**：`chrome://extensions/` → Focus Catcher → "检查视图：Service Worker"

## 下一步计划

- [ ] 添加插件内历史记录查看
- [ ] 支持自定义快捷键
- [ ] 添加捕捉统计图表
- [ ] 支持导出学习报告
- [ ] 支持多种主题样式

## 许可证

MIT License

---

**Enjoy learning with Focus Catcher! 🚀**

