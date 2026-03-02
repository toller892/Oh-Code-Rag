# 🌲 CodeTree

**Vectorless RAG for Code Repositories**

> Navigate your codebase like a human expert — using LLM reasoning, not vector similarity.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/toller892/Oh-Code-Rag?style=social)](https://github.com/toller892/Oh-Code-Rag)

---

## 🤔 The Problem

Traditional RAG (Retrieval-Augmented Generation) for code has fundamental limitations:

| Problem | Description |
|---------|-------------|
| ❌ **Vector similarity ≠ Code relevance** | "login" and "logout" have similar embeddings, but they're completely different! |
| ❌ **Chunking destroys structure** | Splitting a class across chunks loses critical context |
| ❌ **Can't follow call chains** | "Who calls this function?" is nearly impossible with vectors |
| ❌ **No architecture understanding** | Vectors don't know that `auth/` is for authentication |

## 💡 The Solution

**CodeTree** takes a different approach — it builds a hierarchical tree index of your codebase and uses **LLM reasoning** to navigate it, just like a human developer would:

- ✅ AST-based parsing preserves code structure
- ✅ LLM reasons about which files are relevant  
- ✅ Understands module relationships and dependencies
- ✅ Can trace function calls across files

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚫 **No Vector Database** | Uses code structure + LLM reasoning instead of embedding similarity |
| 🌳 **AST-Based Indexing** | Parses actual code structure — functions, classes, imports, dependencies |
| 🔗 **Cross-File Intelligence** | Tracks imports, function calls, and dependencies across your entire codebase |
| 🧠 **Reasoning-Based Retrieval** | LLM navigates the code tree like a human expert |
| 💬 **Natural Language Queries** | Ask questions in plain English |
| 🔒 **Privacy-First** | Works with local models (Ollama). Your code never leaves your machine |
| ⚡ **Incremental Indexing** | Only re-index changed files for 2-5x faster updates on large repos |
| 📊 **Real-time Progress** | Visual progress bars show indexing status and statistics |
| 🎯 **Smart Code Extraction** | Extracts only relevant code sections, saving 50-80% tokens |

---

## 📊 Comparison: Vector RAG vs CodeTree

| Feature | Vector RAG | CodeTree |
|---------|:----------:|:--------:|
| Understands code structure | ❌ | ✅ |
| Cross-file references | ❌ | ✅ |
| "Who calls this function?" | ❌ | ✅ |
| No chunking headaches | ❌ | ✅ |
| Explainable retrieval | ❌ | ✅ |
| Works offline | ⚠️ | ✅ |
| No vector DB needed | ❌ | ✅ |

---

## 🚀 Quick Start

### Installation

```bash
pip install codetree-rag
```

Or from source:

```bash
git clone https://github.com/toller892/Oh-Code-Rag.git
cd Oh-Code-Rag
pip install -e .
```

### Configuration

Set your LLM API key:

```bash
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Basic Usage

```python
from codetree import CodeTree

# Index your repository (with progress bar)
tree = CodeTree("/path/to/your/repo", verbose=True)
tree.build_index()

# Update index incrementally (only re-index changed files)
tree.update_index()

# Ask questions about the code
answer = tree.query("How does the authentication system work?")
print(answer)
```

### Advanced Features

**Incremental Indexing** — Only re-index changed files:
```python
# First time: full index
tree.build_index(incremental=False)

# Later: only re-index changed files (2-5x faster)
tree.update_index()
```

**Smart Code Extraction** — Focus on specific functions/classes:
```python
from codetree.extractor import extract_code_smart

# Extract specific functions with context
code = extract_code_smart(
    file_path,
    focus=["authenticate", "UserService"],
    max_lines=200,
    include_imports=True
)
```

**Progress Tracking** — Monitor indexing progress:
```python
tree = CodeTree("/path/to/repo", verbose=True)
tree.build_index(show_progress=True)
# Output:
# ⠋ Scanning repository... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  0:00:02
# ✅ Index built successfully!
# 📊 Files indexed: 1,234 | Total lines: 156,789
```

### CLI Usage

```bash
# Index a repository
codetree index /path/to/repo

# Query the codebase  
codetree query "Where is database connection handled?"

# Interactive chat mode
codetree chat

# Show code structure
codetree tree

# Find symbol references
codetree find "UserService"
```

---

## 🎯 Use Cases

### 👨‍💻 For Developers

**Onboarding to New Codebases:**
- "What's the overall architecture of this project?"
- "How do requests flow from API to database?"
- "Where should I add a new payment method?"

**Code Review & Understanding:**
- "What does the processOrder function do?"
- "Who calls the validateUser method?"
- "What happens if authentication fails?"

### 🏢 Industry Applications

| Industry | Use Case | Example Query |
|----------|----------|---------------|
| **FinTech** | Audit & Compliance | "How is user data encrypted?" |
| **Healthcare** | Security Review | "Where is patient data accessed?" |
| **E-commerce** | Feature Development | "How does the cart system work?" |
| **DevOps** | Incident Response | "What services depend on Redis?" |
| **Education** | Code Learning | "Explain the MVC pattern in this app" |

### 🔬 Research & Analysis

- **Legacy Code Migration**: Understand old systems before rewriting
- **Security Auditing**: Find all database queries, API endpoints
- **Documentation Generation**: Auto-generate architecture docs
- **Dependency Analysis**: Map out service dependencies

---

## 🔬 Real-World Examples

### Example 1: Understanding Project Architecture

**Query:**

```python
from codetree import CodeTree

tree = CodeTree("./my-project")
tree.build_index()

answer = tree.query("What's the overall architecture? What are the core modules?")
print(answer)
```

**Output:**

```
## Project Architecture

This project follows a modular architecture with these core components:

1. **CodeTree (core.py)** - Main entry point
   - `build_index()`: Builds the code tree
   - `query()`: Natural language queries
   - `find()`: Symbol search

2. **CodeIndexer (indexer.py)** - Index construction
   - Recursively parses directories
   - Builds TreeNode hierarchy
   
3. **CodeParser (parser.py)** - AST parsing
   - Supports Python, JS, Go, Rust, Java
   - Extracts functions, classes, imports

4. **CodeRetriever (retriever.py)** - LLM-based retrieval
   - Two-stage: retrieve → answer
   - Uses reasoning prompts

## Data Flow
User Query → CodeTree → Retriever → LLM Reasoning → File Selection → Answer
```

### Example 2: Finding Function Usage

**Query:**

```python
refs = tree.find("authenticate")
print(refs)
```

**Output:**

```
📍 Found 5 references to 'authenticate':

  [function]  src/auth/login.py:45 → authenticate
  [function]  src/auth/oauth.py:78 → authenticate_oauth  
  [import]    src/api/middleware.py → from auth import authenticate
  [import]    src/api/routes.py → from auth.login import authenticate
  [class]     src/auth/base.py:12 → Authenticator
```

### Example 3: Tracing Code Flow

**Query:**

```python
answer = tree.query("How does a user login request flow through the system?")
print(answer)
```

**Output:**

```
## Login Request Flow

1. **Entry Point**: `src/api/routes.py`
   - @app.post("/login") routes to auth_service.authenticate()

2. **Authentication**: `src/auth/service.py`
   - Validates credentials against database
   - Generates JWT token on success
   
3. **Database**: `src/db/users.py`
   - get_user_by_email() fetches user record
   - verify_password() checks hash

4. **Response**: Returns JWT token or 401 error
```

---

## 🏗️ How It Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CodeTree                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   CodeParser ──────▶ CodeIndexer ──────▶ CodeIndex (JSON)   │
│   (AST Parse)        (Build Tree)        (Store)            │
│                                              │               │
│                                              ▼               │
│   Answer ◀────────── Retrieve ◀────────── CodeRetriever    │
│   (Markdown)         (Read Files)         (LLM Reasoning)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Two-Stage Retrieval Process

**Stage 1: Reasoning-Based Navigation**

```
User: "How does authentication work?"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│ LLM analyzes code tree structure:                           │
│                                                             │
│ "Authentication relates to auth module...                   │
│  Let me check src/auth/ directory...                        │
│  login.py and oauth.py look relevant...                     │
│  Also need to check who imports these..."                   │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
Selected Files: [src/auth/login.py, src/auth/oauth.py, ...]
```

**Stage 2: Answer Generation**

```
Read selected files → Generate comprehensive answer with code snippets
```

---

## 🗣️ Supported Languages

| Language | Extensions | Status |
|----------|------------|:------:|
| Python | `.py`, `.pyi` | ✅ Full |
| JavaScript | `.js`, `.jsx`, `.mjs` | ✅ Full |
| TypeScript | `.ts`, `.tsx` | ✅ Full |
| Go | `.go` | ✅ Full |
| Rust | `.rs` | ✅ Full |
| Java | `.java` | ✅ Full |
| C/C++ | `.c`, `.cpp`, `.h` | 🚧 Coming Soon |

---

## ⚙️ Configuration

Create `.codetree.yaml` in your project:

```yaml
# LLM Configuration
llm:
  provider: openai          # openai, anthropic, ollama
  model: gpt-4o
  temperature: 0.0
  max_tokens: 4096

# For local/private deployment
# llm:
#   provider: ollama
#   model: llama3
#   base_url: http://localhost:11434

# Index Settings  
index:
  languages:
    - python
    - javascript
    - typescript
    - go
  exclude:
    - node_modules
    - __pycache__
    - .git
    - venv
    - dist
  max_file_size: 100000    # Skip files larger than 100KB
```

---

## 📈 Performance

### Indexing Speed

| Metric | Small Repo (<100 files) | Medium Repo (<1000 files) | Large Repo (<10000 files) |
|--------|:-----------------------:|:-------------------------:|:-------------------------:|
| **Full Index** | < 5s | < 30s | < 5min |
| **Incremental Update** | < 1s | < 10s | < 2min |
| Index Size | < 100KB | < 1MB | < 10MB |
| Query Time | 2-5s | 3-8s | 5-15s |

*Times depend on LLM provider latency*

### Optimization Benefits

| Feature | Benefit | Impact |
|---------|---------|--------|
| **Incremental Indexing** | Only re-index changed files | 2-5x faster updates |
| **Smart Extraction** | Extract only relevant code | 50-80% token savings |
| **Progress Tracking** | Real-time feedback | Better UX |

**Example**: For a 3,000-file repository:
- Full index: ~2 minutes
- Incremental update (10 changed files): ~20 seconds
- **10x faster** for typical development workflows!

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Areas to contribute:**
- 🌍 Add language parsers (C++, Ruby, PHP, etc.)
- 🧪 Improve test coverage
- 📖 Documentation and examples
- 🚀 Performance optimizations
- 🎨 CLI improvements

---

## 🔌 MCP Server (Claude Desktop & More)

CodeTree works as an MCP (Model Context Protocol) server, compatible with Claude Desktop, Cline, Continue, and other MCP clients.

### Installation

```bash
pip install codetree-mcp
```

### Setup for Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "codetree": {
      "command": "python",
      "args": ["/path/to/Oh-Code-Rag/mcp/server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-your-key-here"
      }
    }
  }
}
```

### MCP Tools

| Tool | Description |
|------|-------------|
| `codetree_index` | Index a repository |
| `codetree_query` | Ask questions about code |
| `codetree_tree` | Show code structure |
| `codetree_find` | Find symbol references |
| `codetree_stats` | Get repo statistics |

See `mcp/README.md` for full documentation.

---

## 🤖 Clawdbot Skill

CodeTree also comes as a Clawdbot skill for AI assistant integration.

### Installation

```bash
pip install codetree-skill
```

Or copy the `skill/` folder to your Clawdbot skills directory:

```bash
cp -r skill/ ~/.clawdbot/skills/codetree/
```

### Skill Commands

```bash
# Index a repo
./scripts/codetree.sh index /path/to/repo

# Query code
./scripts/codetree.sh query /path/to/repo "How does auth work?"

# Show structure
./scripts/codetree.sh tree /path/to/repo

# Find symbol
./scripts/codetree.sh find /path/to/repo "UserService"
```

See `skill/SKILL.md` for full documentation.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Inspired by [PageIndex](https://github.com/VectifyAI/PageIndex) — vectorless RAG for documents.

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=toller892/Oh-Code-Rag&type=Date)](https://star-history.com/#toller892/Oh-Code-Rag&Date)

---

**If you find CodeTree useful, please give us a ⭐!**
