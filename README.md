# Henry - AI E-commerce Expert Dialogue System

**English** | [日本語](./README_ja.md) | [简体中文](./README_zh.md)

An intelligent e-commerce knowledge base Q&A system powered by local LLMs. It utilizes RAG (Retrieval-Augmented Generation) technology to answer questions related to cross-border e-commerce.

## Key Features

- 🤖 **Multi-Model Support**: Supports multiple LLM providers including OLLAMA (local), OpenAI, and Anthropic.
- 📚 **Knowledge Base Management**: Automatically indexes cross-border e-commerce articles (TikTok, AI tools, finance, etc.).
- 🔍 **Hybrid Search**: Combines semantic search and keyword matching for high accuracy and relevance.
- 💬 **Multi-turn Conversation**: Maintains context for continuous and natural dialogue.
- 📖 **Source Citations**: Automatically cites source articles for every answer to ensure traceability.
- 🌊 **Streaming Response**: Real-time answer generation for a ChatGPT-like experience.
- 🎨 **Advanced Markdown**: Full support for tables, lists, and code syntax highlighting.
- ⚙️ **Web Configuration**: Configure model APIs and knowledge base paths directly in the UI without editing code or environment variables.

## Tech Stack

**Backend:**
- **Python 3.9+**
- **FastAPI**: High-performance REST API with SSE streaming.
- **LlamaIndex**: Robust RAG framework.
- **Qdrant**: High-performance vector database.
- **SQLite**: Lightweight storage for conversation history.
- **HuggingFace Embeddings**: Multilingual pre-trained models.

**Frontend:**
- **Vanilla JavaScript**: Zero-dependency, lightweight implementation.
- **HTML5 + CSS3**: Modern, responsive design.
- **Marked.js & Highlight.js**: Premium Markdown rendering and code highlighting.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Base Services

If you are using local models, ensure that OLLAMA or oMLX is running.

### 3. Start the Server

```bash
./start_server.sh
```

Or start manually:

```bash
python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 4. Access and Configuration

1. Open your browser and navigate to: **http://localhost:8080**
2. Click the **Settings icon** at the top of the sidebar.
3. Configure your LLM API details and the path to your local knowledge base directory.
4. Save the settings, and the system will automatically initialize the resources.

## Project Structure

```
.
├── src/
│   ├── api/              # FastAPI application and routes
│   ├── storage/          # Vector DB and persistence layer
│   ├── indexing/         # Document indexing and preprocessing
│   ├── search/           # Search engine logic
│   ├── rag/              # Core RAG processes
│   └── llm/              # LLM client integration
├── frontend/             # Frontend static assets
├── data/                 # Database and config files
└── tests/                # Automated tests
```

## License

MIT License

## Author

Built with GSD (Get Shit Done) workflow
