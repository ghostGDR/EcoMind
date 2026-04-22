# EcoMind - AI E-commerce Expert Dialogue System

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

## Quick Start

### Installation

#### macOS (Homebrew)
```bash
brew tap ecomind/tap
brew install ecomind
```

#### Windows / Linux (NPM)
```bash
npm install -g ecomind-ai
```

#### Running the App
Once installed, simply run:
```bash
ecomind start
```

This will automatically set up the Python environment and launch the server at **http://localhost:8080**.

### Prerequisites

- **Node.js** (v16+)
- **Python 3.9+**
- **OLLAMA** or **oMLX** (if using local LLMs)

## Manual Installation

If you prefer to set up the environment manually:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd EcoMind
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   ./start_ecomind.sh
   ```

## Setup & Configuration

Once the web interface is open (**http://localhost:8080**):
1. Click the **Gear Icon (⚙️)** in the sidebar header.
2. **Provider**: Select `OLLAMA / oMLX` for local or `OpenAI`/`Anthropic` for cloud models.
3. **Model**: Enter the model string (e.g., `Qwen3-Coder-30B-A3B-Instruct-4bit`).
4. **Base URL**: For local oMLX, use `http://127.0.0.1:8000`.
5. **Wiki Path**: Enter the absolute path to your documents folder.
6. **Save**: Click "Save Configuration". The system will automatically index your documents.

## Project Structure

```
.
├── bin/              # CLI scripts (Node.js)
├── src/
│   ├── api/          # FastAPI application and routes
│   ├── storage/      # Vector DB and persistence layer
│   ├── indexing/     # Document indexing and preprocessing
│   ├── search/       # Search engine logic
│   ├── rag/          # Core RAG processes
│   └── llm/          # LLM client integration
├── frontend/         # Frontend static assets
├── data/             # Database and config files
└── docs/             # Documentation in multiple languages
```

## License

MIT License

## Author

Built with EcoMind team
