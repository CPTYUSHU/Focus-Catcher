# 项目文件结构说明

## 📁 文件夹组织

```
fastapiapp/
├── main.py                    # 主应用程序
├── requirements.txt           # Python 依赖
├── start.sh                   # 主启动脚本 ⭐
├── README.md                  # 项目说明
├── .env                       # 环境变量（需手动创建）
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略规则
│
├── docs/                      # 📚 文档目录
│   ├── QUICK_START.md        # 快速开始指南
│   ├── AGENTIC_LOOP.md       # Agentic Loop 详解
│   ├── TOOL_CALLING.md       # 工具调用文档
│   ├── READ_PAGE_TOOL.md     # read_page 工具文档
│   ├── DEBUG_GUIDE.md        # 调试指南
│   ├── SUMMARY.md            # 项目总结
│   └── PROJECT_STRUCTURE.md  # 本文件
│
├── tests/                     # 🧪 测试脚本目录
│   ├── test_agentic_loop.py  # Agentic Loop 测试
│   ├── test_read_page.py     # 多工具测试
│   └── test_tool_calling.py  # 工具调用测试
│
└── scripts/                   # 🔧 实用脚本目录
    ├── start_server.sh       # 服务器启动脚本（旧版）
    └── run_dev.sh            # 开发模式脚本
```

## 📂 目录说明

### 根目录
存放核心应用文件和配置：

- **`main.py`** - FastAPI 应用主文件
  - 包含所有工具函数（web_search, read_page）
  - Agentic Loop 实现
  - API 端点定义

- **`requirements.txt`** - Python 依赖列表
  - FastAPI, OpenAI SDK, BeautifulSoup 等

- **`start.sh`** - 推荐的启动脚本
  - 自动加载 .env 文件
  - 启动开发服务器

- **`.env`** - 环境变量（需手动创建）
  - 存储 API 密钥
  - 不提交到 Git

- **`.gitignore`** - Git 忽略规则
  - 排除 .env, __pycache__ 等

### 📚 docs/ - 文档目录

所有项目文档集中存放：

| 文件 | 用途 |
|------|------|
| `QUICK_START.md` | 5分钟快速入门 |
| `AGENTIC_LOOP.md` | Agentic Loop 实现详解 |
| `TOOL_CALLING.md` | 工具调用基础文档 |
| `READ_PAGE_TOOL.md` | read_page 工具说明 |
| `DEBUG_GUIDE.md` | 调试和消息历史指南 |
| `SUMMARY.md` | 完整项目总结 |
| `PROJECT_STRUCTURE.md` | 本文件 |

**新增文档规则：**
- 所有 `.md` 文档文件应放在 `docs/` 目录
- 文档命名使用大写加下划线（如 `NEW_FEATURE.md`）

### 🧪 tests/ - 测试目录

所有测试脚本集中存放：

| 文件 | 用途 |
|------|------|
| `test_agentic_loop.py` | 测试完整的 Agentic Loop |
| `test_read_page.py` | 测试多工具协作 |
| `test_tool_calling.py` | 测试基础工具调用 |

**运行测试：**
```bash
# 从项目根目录运行
python tests/test_agentic_loop.py
python tests/test_read_page.py
python tests/test_tool_calling.py
```

**新增测试规则：**
- 所有测试脚本应放在 `tests/` 目录
- 测试文件命名以 `test_` 开头
- 测试脚本应可从项目根目录运行

### 🔧 scripts/ - 脚本目录

实用工具脚本集中存放：

| 文件 | 用途 |
|------|------|
| `start_server.sh` | 启动服务器（旧版，保留兼容） |
| `run_dev.sh` | 开发模式启动脚本 |

**新增脚本规则：**
- 所有 shell 脚本应放在 `scripts/` 目录
- 脚本应添加执行权限（`chmod +x`）
- 脚本应包含使用说明注释

## 🚀 快速开始

### 1. 启动服务器

**推荐方式（从根目录）：**
```bash
./start.sh
```

**或使用 scripts 中的脚本：**
```bash
./scripts/start_server.sh
```

### 2. 运行测试

```bash
# 完整的 Agentic Loop 测试
python tests/test_agentic_loop.py

# 多工具测试
python tests/test_read_page.py
```

### 3. 查看文档

```bash
# 快速开始
cat docs/QUICK_START.md

# 调试指南
cat docs/DEBUG_GUIDE.md

# 项目总结
cat docs/SUMMARY.md
```

## 📝 文件添加指南

### 添加新文档

```bash
# 创建新文档
vim docs/NEW_FEATURE.md

# 或使用编辑器
code docs/NEW_FEATURE.md
```

### 添加新测试

```bash
# 创建新测试
vim tests/test_new_feature.py

# 添加执行权限
chmod +x tests/test_new_feature.py
```

### 添加新脚本

```bash
# 创建新脚本
vim scripts/deploy.sh

# 添加执行权限
chmod +x scripts/deploy.sh
```

## 🎯 文件组织原则

### ✅ 应该做的

1. **文档** → `docs/`
2. **测试** → `tests/`
3. **脚本** → `scripts/`
4. **核心代码** → 根目录
5. **配置文件** → 根目录

### ❌ 不应该做的

1. ❌ 不要在根目录堆积文档文件
2. ❌ 不要混合测试和应用代码
3. ❌ 不要将脚本散落在各处
4. ❌ 不要创建过深的目录层级

## 🔄 迁移说明

如果您有旧的项目结构，可以这样迁移：

```bash
# 移动文档
mv *.md docs/
mv README.md .  # README 保留在根目录

# 移动测试
mv test_*.py tests/

# 移动脚本
mv *.sh scripts/
mv start.sh .  # 主启动脚本保留在根目录
```

## 📊 目录统计

- **根目录文件**: 7 个（核心文件）
- **文档文件**: 7 个（docs/）
- **测试脚本**: 3 个（tests/）
- **实用脚本**: 2 个（scripts/）

**总计**: 19 个文件，组织清晰！

## 🎨 最佳实践

1. **保持根目录整洁** - 只放核心文件
2. **文档集中管理** - 便于查找和维护
3. **测试独立存放** - 清晰的测试结构
4. **脚本统一位置** - 方便管理和执行
5. **命名规范一致** - 易于识别文件用途

## 🔗 相关文档

- [快速开始](QUICK_START.md) - 5分钟上手
- [项目总结](SUMMARY.md) - 完整功能说明
- [调试指南](DEBUG_GUIDE.md) - 如何调试

---

**保持项目结构清晰，让开发更高效！** 🚀

