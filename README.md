# 🌲 CodeTree

**Vectorless RAG for Code Repositories** - Navigate your codebase like a human expert.

CodeTree builds a hierarchical tree index from your code repository and uses LLM reasoning for intelligent code retrieval. No vector database, no embeddings, no chunking - just pure reasoning.

## ✨ Features

- **🚫 No Vector DB**: Uses code structure and LLM reasoning, not semantic similarity
- **🌳 AST-based Indexing**: Understands code structure (classes, functions, imports)
- **🔗 Cross-file References**: Tracks function calls and dependencies across files
- **🧠 Reasoning-based Retrieval**: LLM navigates the code tree to find relevant code
- **💬 Natural Language Queries**: Ask questions in plain English
- **🔒 Privacy-friendly**: Works with local models (Ollama) or cloud APIs

## 🚀 Quick Start

### Installation

```bash
pip install codetree-rag
```

Or install from source:

```bash
git clone https://github.com/YOUR_USERNAME/codetree.git
cd codetree
pip install -e .
```

### Basic Usage

```python
from codetree import CodeTree

# Index a repository
tree = CodeTree("/path/to/your/repo")
tree.build_index()

# Ask questions about the code
answer = tree.query("How does the authentication system work?")
print(answer)

# Find specific functionality
answer = tree.query("Where is the database connection handled?")
print(answer)
```

### CLI Usage

```bash
# Index a repository
codetree index /path/to/repo

# Query the codebase
codetree query "How does error handling work?"

# Interactive mode
codetree chat
```

## 🔧 Configuration

Create a `.codetree.yaml` in your project root or use environment variables:

```yaml
# LLM Configuration
llm:
  provider: openai  # openai, anthropic, ollama
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}

# For local models
# llm:
#   provider: ollama
#   model: llama3
#   base_url: http://localhost:11434

# Index settings
index:
  languages: [python, javascript, typescript, go, rust]
  exclude: [node_modules, __pycache__, .git, venv]
  max_file_size: 100000  # bytes
```

## 🏗️ How It Works

### 1. Parse & Index
```
Repository
    ├── src/
    │   ├── auth/
    │   │   ├── login.py      → Functions: login(), verify_token()
    │   │   └── oauth.py      → Classes: OAuthHandler
    │   ├── database/
    │   │   └── connection.py → Functions: connect(), query()
    │   └── api/
    │       └── routes.py     → Functions: get_users(), create_user()
    └── tests/
        └── test_auth.py      → Functions: test_login()

        ↓ AST Parsing ↓

CodeTree Index (JSON):
{
  "root": {
    "name": "myproject",
    "type": "directory",
    "summary": "Web API with auth and database",
    "children": [
      {
        "name": "auth",
        "summary": "Authentication module with login and OAuth",
        "functions": ["login", "verify_token"],
        "classes": ["OAuthHandler"],
        "imports": ["database.connection"],
        ...
      }
    ]
  }
}
```

### 2. Reasoning-based Retrieval
```
Query: "How does user authentication work?"
    ↓
LLM reasons over tree index:
  → "Authentication" relates to auth module
  → Check auth/login.py and auth/oauth.py
  → Also check what calls these functions
    ↓
Retrieves relevant code sections
    ↓
LLM generates answer with code references
```

## 📊 Comparison

| Feature | Vector RAG | CodeTree |
|---------|-----------|----------|
| Understands code structure | ❌ | ✅ |
| Cross-file references | ❌ | ✅ |
| Semantic chunking | Manual tuning | Automatic (AST) |
| Retrieval method | Similarity | Reasoning |
| Explainability | Low | High |
| Local-first | Depends | ✅ |

## 🗣️ Supported Languages

- ✅ Python
- ✅ JavaScript / TypeScript
- ✅ Go
- ✅ Rust
- ✅ Java
- 🚧 C / C++ (coming soon)

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Inspired by [PageIndex](https://github.com/VectifyAI/PageIndex) - vectorless RAG for documents.

---

⭐ **Star us on GitHub if you find this useful!**
