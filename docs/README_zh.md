# EcoMind - AI 电商专家对话系统

[English](../README.md) | [日本語](./README_ja.md) | **简体中文**

基于本地 LLM 的智能电商知识库问答系统，使用 RAG (检索增强生成) 技术回答跨境电商相关问题。

## 功能特性

- 🤖 **多模型支持**: 支持 OLLAMA (本地), OpenAI, Anthropic 等多种 LLM 提供商
- 📚 **知识库管理**: 自动索引跨境电商相关文章（TikTok、AI 工具、财务等）
- 🔍 **混合检索**: 语义搜索 + 关键词匹配，确保回答的准确性与相关性
- 💬 **多轮对话**: 具备上下文记忆能力，支持连续追问
- 📖 **来源引用**: 自动标注回答来源，确保信息可追溯
- 🌊 **流式响应**: 实时显示 AI 回答，类似 ChatGPT 的极致体验
- 🎨 **高级 Markdown**: 支持表格、列表、数学公式及代码语法高亮
- ⚙️ **网页配置**: 无需修改代码或环境变量，直接在网页端配置模型接口与知识库路径

## 快速开始

### 安装方法

#### macOS (Homebrew)
```bash
brew tap ecomind/tap
brew install ecomind
```

#### Windows / Linux (NPM)
```bash
npm install -g ecomind-ai
```

#### 启动程序
安装完成后，只需运行：
```bash
ecomind start
```

系统将自动为您配置 Python 环境并在 **http://localhost:8080** 启动服务器。

### 准备工作

- **Node.js** (v16+)
- **Python 3.9+**
- **OLLAMA** 或 **oMLX** (如果您使用本地 LLM)

## 手动安装 (开发者)

如果您希望手动配置环境：

1. **克隆仓库**:
   ```bash
   git clone <repository-url>
   cd EcoMind
   ```

2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

3. **启动服务器**:
   ```bash
   ./start_ecomind.sh
   ```

## 系统配置

打开网页界面后 (**http://localhost:8080**):
1. 点击侧边栏顶部的**齿轮图标 (⚙️)**。
2. **提供商 (Provider)**: 本地模型选择 `OLLAMA / oMLX`，云端模型选择 `OpenAI` 或 `Anthropic`。
3. **模型名称 (Model)**: 输入模型标识符（如 `Qwen3-Coder-30B-A3B-Instruct-4bit`）。
4. **基础 URL (Base URL)**: 对于本地 oMLX，使用 `http://127.0.0.1:8000`。
5. **知识库路径 (Wiki Path)**: 输入文档文件夹的**绝对路径**。
6. **保存**: 点击“保存配置”。系统将自动为您的文档建立索引。

## 项目结构

```
.
├── bin/              # CLI 脚本 (Node.js)
├── src/              # 后端 Python 代码
├── frontend/         # 前端静态资源
├── data/             # 数据库与配置文件
└── docs/             # 多语言文档
```

## 许可证

MIT License
