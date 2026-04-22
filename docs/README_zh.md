# Henry - AI 电商专家对话系统

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

## 技术栈

**后端:**
- **Python 3.9+**
- **FastAPI**: 高性能 REST API 与 SSE 流式传输
- **LlamaIndex**: 强大的 RAG 框架
- **Qdrant**: 高性能向量数据库
- **SQLite**: 轻量级对话历史存储
- **HuggingFace Embeddings**: 使用多语言预训练模型

**前端:**
- **Vanilla JavaScript**: 纯原生开发，零框架负担
- **HTML5 + CSS3**: 现代响应式设计
- **Marked.js & Highlight.js**: 优质的 Markdown 渲染与代码高亮

## 快速开始

### 准备工作

- **Python 3.9+**
- **OLLAMA** 或 **oMLX** (用于本地 LLM 推理)
- **知识库**: 一个包含 `.md` 或 `.xlsx` 文件的文件夹，用于系统学习。

### 1. 安装

克隆仓库并安装必要的依赖：

```bash
git clone <repository-url>
cd gsd_test
pip install -r requirements.txt
```

### 2. 启动本地 LLM 服务

如果您打算使用本地模型，请启动推理引擎（例如 OLLAMA 或 oMLX）：

```bash
# oMLX 示例
/Applications/oMLX.app/Contents/MacOS/omlx-cli launch
```

### 3. 启动 Henry

运行启动脚本以启动 FastAPI 服务器：

```bash
./start_server.sh
```

服务器将运行在 **http://localhost:8080**。

### 4. 系统配置

打开网页界面后：
1. 点击侧边栏顶部的**齿轮图标 (⚙️)**。
2. **提供商 (Provider)**: 本地模型选择 `OLLAMA / oMLX`，云端模型选择 `OpenAI` 或 `Anthropic`。
3. **模型名称 (Model)**: 输入模型标识符（如 `Qwen3-Coder-30B-A3B-Instruct-4bit`）。
4. **基础 URL (Base URL)**: 对于本地 oMLX，使用 `http://127.0.0.1:8000`。
5. **知识库路径 (Wiki Path)**: 输入文档文件夹的**绝对路径**。
6. **保存**: 点击“保存配置”。系统将自动初始化向量数据库并为您的文档建立索引。

### 5. 开始对话！

现在您可以开始提问了。Henry 将根据您的文档提供带引用的回答，并支持精美的 Markdown 格式。

## 项目结构

```
.
├── src/
│   ├── api/              # FastAPI 应用与路由
│   ├── storage/          # 向量数据库与持久化层
│   ├── indexing/         # 文档索引与预处理
│   ├── search/           # 搜索引擎逻辑
│   ├── rag/              # RAG 核心流程
│   └── llm/              # LLM 客户端集成
├── frontend/             # 前端静态资源
├── data/                 # 数据库与配置文件
└── tests/                # 自动化测试
```

## 许可证

MIT License

## 作者

基于 GSD (Get Shit Done) 工作流构建
