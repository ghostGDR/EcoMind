# Phase 1: Data Layer Foundation - Research

**Phase:** 1
**Created:** 2026-04-22
**Researcher:** gsd-phase-researcher (inline)

## Research Question

如何为 Henry AI 对话系统建立持久化存储基础设施，支持向量搜索和对话历史管理？

## Standard Stack

### Vector Database: Qdrant

**Library:** `qdrant-client` (Python)
**Why Qdrant:**
- 本地部署支持（符合数据隐私要求）
- 性能优势：2-4x RPS compared to alternatives
- 原生支持混合检索（语义 + 关键词）
- 与 LlamaIndex 深度集成

**Installation:**
```bash
pip install qdrant-client
```

**Local Mode Options:**
1. **In-memory mode** (开发/测试): `QdrantClient(":memory:")`
2. **Persistent mode** (生产): `QdrantClient(path="path/to/db")`

**Key Operations:**
- Create collection with vector config
- Upload vectors with payloads (metadata)
- Query by vector similarity
- Support for batch operations (parallel upload)

### Conversation Storage: SQLite

**Library:** Python built-in `sqlite3` + optional `sqlite-utils` for convenience
**Why SQLite:**
- 零配置，文件级数据库
- 本地存储，符合隐私要求
- 足够支持单用户对话历史
- Python 标准库内置支持

**Alternative considered:** `sqlite-utils` by Simon Willison
- 提供更友好的 API
- 支持全文搜索配置
- 简化 schema 迁移

### RAG Framework: LlamaIndex

**Library:** `llama-index` (formerly GPT Index)
**Why LlamaIndex:**
- 专为 RAG 系统设计
- 原生 Qdrant 集成
- 文档加载器生态系统丰富
- 支持多种 LLM 后端（Claude, OpenAI）
- 中文支持良好

**Core Components:**
- `VectorStoreIndex`: 主索引类
- `QdrantVectorStore`: Qdrant 适配器
- `StorageContext`: 存储配置
- `SimpleDirectoryReader`: 文档加载器

## Architecture Patterns

### 1. Three-Layer Storage Architecture

```
┌─────────────────────────────────────┐
│  Application Layer                  │
│  (FastAPI / Business Logic)         │
└─────────────────────────────────────┘
           │
           ├──────────────┬──────────────┐
           ▼              ▼              ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Qdrant     │  │   SQLite     │  │  File System │
│  (Vectors)   │  │ (Conversations)│ │  (Documents) │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Separation of Concerns:**
- **Qdrant**: 向量嵌入 + 语义搜索
- **SQLite**: 对话历史 + 用户反馈
- **File System**: 原始文档存储（`/Users/a1234/wiki/raw/articles`）

### 2. LlamaIndex Integration Pattern

```python
# Standard initialization pattern
import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore

# 1. Initialize Qdrant client
client = qdrant_client.QdrantClient(path="./data/qdrant_db")

# 2. Create vector store wrapper
vector_store = QdrantVectorStore(
    client=client, 
    collection_name="henry_knowledge_base"
)

# 3. Create storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# 4. Build index from documents
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
)
```

### 3. Document Storage Interface Pattern

**Recommended Approach:**
- 直接读取文件系统（不复制文档）
- 使用 `SimpleDirectoryReader` 加载文档
- 保持原始文档路径引用（用于来源追溯）

```python
from llama_index.core import SimpleDirectoryReader

# Load documents from user's wiki directory
documents = SimpleDirectoryReader(
    "/Users/a1234/wiki/raw/articles"
).load_data()
```

## Don't Hand-Roll

### ❌ 不要自己实现的功能

1. **向量相似度搜索算法**
   - Qdrant 已优化 HNSW 索引
   - 自己实现性能差且容易出错

2. **文档分块策略**
   - LlamaIndex 提供智能分块（`Settings.chunk_size`）
   - 支持语义边界保持

3. **嵌入模型管理**
   - LlamaIndex 自动处理嵌入生成
   - 支持多种嵌入模型（OpenAI, HuggingFace, etc.）

4. **向量存储抽象层**
   - 使用 LlamaIndex 的 `VectorStore` 接口
   - 未来切换向量数据库无需重写代码

## Common Pitfalls

### 1. Qdrant Collection Configuration

**问题:** 创建 collection 时未指定正确的 vector size
**后果:** 上传向量时报错 "dimension mismatch"
**解决:**
```python
# 必须匹配嵌入模型的输出维度
# 例如: sentence-transformers/all-MiniLM-L6-v2 = 384 dimensions
client.create_collection(
    "collection_name",
    vectors_config=models.VectorParams(
        size=384,  # 必须与嵌入模型匹配
        distance=models.Distance.COSINE
    )
)
```

### 2. SQLite Concurrency

**问题:** SQLite 默认不支持高并发写入
**后果:** 多个请求同时写入时出现 "database is locked" 错误
**解决:**
- Phase 1 单用户场景无需担心
- 未来如需并发：使用 WAL mode (`PRAGMA journal_mode=WAL`)

### 3. File Path Handling

**问题:** 硬编码绝对路径导致跨环境问题
**后果:** 部署到其他机器时路径失效
**解决:**
```python
import os
from pathlib import Path

# 使用配置文件或环境变量
WIKI_PATH = os.getenv("WIKI_PATH", "/Users/a1234/wiki/raw/articles")
documents = SimpleDirectoryReader(WIKI_PATH).load_data()
```

### 4. Qdrant Persistence

**问题:** 使用 `:memory:` 模式导致重启后数据丢失
**后果:** 每次重启需要重新索引所有文档
**解决:**
```python
# 开发环境可以用 :memory:
# 生产环境必须指定持久化路径
client = QdrantClient(path="./data/qdrant_db")  # ✓ 持久化
# client = QdrantClient(":memory:")  # ✗ 仅用于测试
```

## Code Examples

### Example 1: Initialize Qdrant with LlamaIndex

```python
import qdrant_client
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import SimpleDirectoryReader

# Configure chunk size for Chinese text
Settings.chunk_size = 512  # 中文文本建议 512-1024

# Initialize Qdrant client (persistent mode)
client = qdrant_client.QdrantClient(path="./data/qdrant_db")

# Create vector store
vector_store = QdrantVectorStore(
    client=client, 
    collection_name="henry_docs"
)

# Create storage context
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Load documents
documents = SimpleDirectoryReader(
    "/Users/a1234/wiki/raw/articles"
).load_data()

# Build index
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
)
```

### Example 2: SQLite Conversation Storage Schema

```python
import sqlite3
from datetime import datetime

# Initialize database
conn = sqlite3.connect('./data/conversations.db')
cursor = conn.cursor()

# Create conversations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    title TEXT
)
''')

# Create messages table
cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
)
''')

# Create sources table (for citation tracking)
cursor.execute('''
CREATE TABLE IF NOT EXISTS message_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,
    document_path TEXT NOT NULL,
    chunk_text TEXT,
    relevance_score REAL,
    FOREIGN KEY (message_id) REFERENCES messages(id)
)
''')

conn.commit()
conn.close()
```

### Example 3: Document Storage Interface

```python
from pathlib import Path
from typing import List
from llama_index.core import SimpleDirectoryReader

class DocumentStorage:
    """Interface for reading documents from file system"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    def load_all_documents(self):
        """Load all documents from the wiki directory"""
        reader = SimpleDirectoryReader(
            str(self.base_path),
            recursive=True,
            required_exts=[".md", ".xlsx"]  # Markdown and Excel
        )
        return reader.load_data()
    
    def list_documents(self) -> List[Path]:
        """List all document files"""
        md_files = list(self.base_path.glob("**/*.md"))
        excel_files = list(self.base_path.glob("**/*.xlsx"))
        return md_files + excel_files
    
    def get_document_metadata(self, file_path: Path) -> dict:
        """Extract metadata from document"""
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "modified": file_path.stat().st_mtime,
        }

# Usage
storage = DocumentStorage("/Users/a1234/wiki/raw/articles")
documents = storage.load_all_documents()
print(f"Loaded {len(documents)} documents")
```

## Dependencies

### Required Packages

```txt
# Vector database
qdrant-client>=1.7.0

# RAG framework
llama-index>=0.9.0
llama-index-vector-stores-qdrant>=0.1.0

# LLM integration (choose one or both)
llama-index-llms-anthropic>=0.1.0  # For Claude
llama-index-llms-openai>=0.1.0     # For OpenAI

# Document processing
python-magic>=0.4.27  # File type detection
openpyxl>=3.1.0       # Excel file support

# Database (built-in)
# sqlite3 is part of Python standard library
```

### Optional Packages

```txt
# Enhanced SQLite utilities
sqlite-utils>=3.35

# Better file watching (for Phase 9)
watchdog>=3.0.0
```

## Validation Architecture

### Dimension 1: Functional Correctness

**Test Strategy:**
- Unit tests for each storage component
- Integration tests for cross-component operations

**Key Tests:**
1. Qdrant can store and retrieve vectors
2. SQLite can persist conversation history
3. Document storage can read from file system

### Dimension 2: Data Integrity

**Test Strategy:**
- Verify data persistence across restarts
- Check foreign key constraints in SQLite

**Key Tests:**
1. Qdrant data survives process restart
2. SQLite foreign keys enforce referential integrity
3. Document paths remain valid

### Dimension 3: Performance

**Test Strategy:**
- Benchmark vector search latency
- Measure database query performance

**Key Tests:**
1. Vector search < 100ms for 1000 documents
2. Conversation history query < 50ms
3. Document loading < 2s for 22 files

### Dimension 4: Error Handling

**Test Strategy:**
- Test with missing directories
- Test with corrupted files
- Test with invalid database states

**Key Tests:**
1. Graceful handling of missing wiki directory
2. Error messages for unsupported file types
3. Database connection retry logic

## Security Considerations

### Data Privacy

**Requirement:** 所有数据本地存储，不上传到第三方服务

**Implementation:**
- Qdrant 本地模式（无网络连接）
- SQLite 文件级数据库（本地文件系统）
- 文档直接从本地路径读取

**Verification:**
- 确认 Qdrant 未配置远程服务器
- 确认无网络请求到向量数据库服务商
- 确认 LLM API 调用仅发送查询和检索结果（不发送原始文档）

### File System Access

**Risk:** 读取用户文件系统的敏感数据

**Mitigation:**
- 限制读取路径到 `/Users/a1234/wiki/raw/articles`
- 使用 Path validation 防止路径遍历攻击
- 不允许用户通过 API 指定任意文件路径

## Open Questions

1. **嵌入模型选择:**
   - 使用 OpenAI embeddings (需要 API) 还是本地模型？
   - 中文支持：OpenAI text-embedding-3-small vs HuggingFace multilingual models
   - **建议:** Phase 1 使用 OpenAI embeddings（简单可靠），Phase 11 优化时考虑本地模型

2. **数据库文件位置:**
   - 使用项目目录 `./data/` 还是用户目录 `~/.henry/`？
   - **建议:** 使用 `./data/` 便于开发，通过环境变量配置

3. **Excel 文件处理:**
   - LlamaIndex 是否原生支持 Excel？需要预处理吗？
   - **需要验证:** Phase 2 实现时测试 `SimpleDirectoryReader` 对 Excel 的支持

## Confidence Levels

| Domain | Confidence | Notes |
|--------|-----------|-------|
| Qdrant setup | High | 官方文档清晰，LlamaIndex 集成成熟 |
| SQLite schema | High | 标准关系型数据库设计 |
| LlamaIndex integration | High | 官方示例丰富，社区活跃 |
| Document loading | Medium | Excel 支持需要验证 |
| Chinese text handling | Medium | 需要测试分块策略对中文的效果 |

## Next Steps for Planning

1. **Plan 01:** 初始化 Qdrant 数据库（本地持久化模式）
2. **Plan 02:** 初始化 SQLite 数据库（创建 schema）
3. **Plan 03:** 实现文档存储接口（读取 wiki 目录）
4. **Plan 04:** 集成测试（验证三层存储协同工作）

---
*Research completed: 2026-04-22*
*Confidence: High (standard stack, well-documented)*
