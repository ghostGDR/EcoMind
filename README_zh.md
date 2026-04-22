# Henry - AI 电商专家对话系统

[English](./README.md) | [日本語](./README_ja.md) | **简体中文**

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

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动基础服务

如果您使用本地模型，请确保 OLLAMA 或 oMLX 已启动。

### 3. 启动服务器

```bash
./start_server.sh
```

或手动启动：

```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. 访问与配置

1. 打开浏览器访问：**http://localhost:8080**
2. 点击侧边栏顶部的**设置图标**。
3. 配置您的 LLM 接口地址、模型名称以及本地知识库目录路径。
4. 保存配置后，系统会自动加载资源。

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
