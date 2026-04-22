# Henry - AI E-commerce Expert Dialogue System

**English** | [日本語](./docs/README_ja.md) | [简体中文](./docs/README_zh.md)

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

### Prerequisites

- **Python 3.9+**
- **OLLAMA** or **oMLX** (for local LLM inference)
- **Knowledge Base**: A folder containing `.md` or `.xlsx` files you want Henry to learn from.

### 1. Installation

Clone the repository and install the required dependencies:

```bash
git clone <repository-url>
cd gsd_test
pip install -r requirements.txt
```

### 2. Start Local LLM Service

If you plan to use local models, start your inference engine (e.g., OLLAMA or oMLX):

```bash
# Example for oMLX
/Applications/oMLX.app/Contents/MacOS/omlx-cli launch
```

### 3. Launch Henry

Run the startup script to launch the FastAPI server:

```bash
./start_server.sh
```

The server will be available at **http://localhost:8080**.

### 4. Setup & Configuration

Once the web interface is open:
1. Click the **Gear Icon (⚙️)** in the sidebar header.
2. **Provider**: Select `OLLAMA / oMLX` for local or `OpenAI`/`Anthropic` for cloud models.
3. **Model**: Enter the model string (e.g., `Qwen3-Coder-30B-A3B-Instruct-4bit`).
4. **Base URL**: For local oMLX, use `http://127.0.0.1:8000`.
5. **Wiki Path**: Enter the absolute path to your documents folder (e.g., `/Users/yourname/documents`).
6. **Save**: Click "Save Configuration". The system will automatically initialize the vector store and index your documents.

### 5. Start Chatting!

You can now ask questions about your documents. Henry will provide answers with citations and beautiful markdown formatting.

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
