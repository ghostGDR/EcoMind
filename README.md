# Henry - AI 电商专家对话系统

基于本地 LLM 的智能电商知识库问答系统，使用 RAG 技术回答跨境电商相关问题。

## 功能特性

- 🤖 **本地 LLM**: 使用 Qwen3-Coder-30B 模型，数据完全本地化
- 📚 **知识库管理**: 索引 22 篇跨境电商文章（TikTok、AI 工具、财务等）
- 🔍 **混合检索**: 语义搜索 + 关键词匹配，提升准确度
- 💬 **多轮对话**: 记住上下文，支持连续提问
- 📖 **来源引用**: 每个回答都引用具体的来源文章
- 🌊 **流式响应**: 实时显示 AI 回答，类似 ChatGPT 体验
- 🎨 **中文界面**: 完全中文化的用户界面

## 技术栈

**后端:**
- Python 3.9+
- FastAPI (REST API + SSE)
- LlamaIndex (RAG 框架)
- Qdrant (向量数据库)
- SQLite (对话历史)
- HuggingFace Embeddings (sentence-transformers)

**前端:**
- Vanilla JavaScript (零依赖)
- HTML5 + CSS3
- Server-Sent Events (SSE)

**LLM:**
- OLLAMA (本地推理)
- Qwen3-Coder-30B-A3B-Instruct-4bit

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# LLM 配置
LLM_PROVIDER=ollama
LLM_MODEL=Qwen3-Coder-30B-A3B-Instruct-4bit
OLLAMA_BASE_URL=http://127.0.0.1:8000

# 知识库路径
WIKI_PATH=/Users/a1234/wiki/raw/articles
```

### 3. 启动 OLLAMA 服务

```bash
/Applications/oMLX.app/Contents/MacOS/omlx-cli launch
```

### 4. 索引知识库（首次运行）

```bash
python3 -m src.indexing.index_wiki
```

### 5. 启动 Henry 服务器

```bash
./start_server.sh
```

或手动启动：

```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 6. 访问界面

打开浏览器访问：**http://localhost:8080**

## API 文档

启动服务器后，访问 Swagger UI 文档：

**http://localhost:8080/docs**

### 主要端点

**对话管理:**
- `POST /api/conversations` - 创建新对话
- `GET /api/conversations` - 列出所有对话
- `GET /api/conversations/{id}` - 获取对话详情

**聊天:**
- `POST /api/chat` - 发送消息（SSE 流式响应）

**文档管理:**
- `GET /api/documents` - 列出所有文档
- `GET /api/documents/topics` - 按主题分类
- `GET /api/documents/search` - 语义搜索

**系统:**
- `GET /health` - 健康检查

## 项目结构

```
.
├── src/
│   ├── api/              # FastAPI 应用
│   │   ├── main.py       # 主应用
│   │   ├── routes/       # API 路由
│   │   ├── models.py     # Pydantic 模型
│   │   └── dependencies.py
│   ├── storage/          # 存储层
│   │   ├── vector_store.py      # Qdrant 向量存储
│   │   ├── conversation_store.py # SQLite 对话存储
│   │   └── document_store.py    # 文档加载
│   ├── indexing/         # 文档索引
│   │   ├── document_indexer.py
│   │   └── index_wiki.py
│   ├── search/           # 搜索引擎
│   │   └── search_engine.py
│   ├── rag/              # RAG 引擎
│   │   ├── query_engine.py
│   │   ├── conversation_manager.py
│   │   └── citation_formatter.py
│   └── llm/              # LLM 客户端
│       ├── llm_client.py
│       └── prompts.py
├── frontend/             # 前端界面
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/                 # 数据目录
│   ├── qdrant_db/        # 向量数据库
│   └── conversations.db  # 对话历史
├── tests/                # 测试
└── .planning/            # GSD 项目规划

```

## 使用示例

### 1. 创建对话

```bash
curl -X POST http://localhost:8080/api/conversations
```

### 2. 发送消息（流式响应）

```bash
curl -N -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "TikTok 广告投放的最佳时间是什么？"
  }'
```

### 3. 搜索文档

```bash
curl "http://localhost:8080/api/documents/search?query=TikTok广告&top_k=5"
```

## 开发

### 运行测试

```bash
pytest tests/
```

### 代码结构

- **存储层**: 向量数据库、对话历史、文档加载
- **索引层**: 文档解析、分块、向量化
- **搜索层**: 语义搜索、混合检索
- **RAG 层**: 检索增强生成、对话管理、引用格式化
- **API 层**: REST 端点、SSE 流式传输
- **前端**: 单页应用、对话界面

## 故障排除

### 问题：无法连接到 OLLAMA

确保 OLLAMA 服务正在运行：

```bash
curl http://127.0.0.1:8000/health
```

### 问题：找不到知识库文件

检查 `.env` 中的 `WIKI_PATH` 是否正确：

```bash
ls $WIKI_PATH
```

### 问题：向量数据库为空

重新索引知识库：

```bash
python3 -m src.indexing.index_wiki
```

## 许可证

MIT License

## 作者

Built with GSD (Get Shit Done) workflow
