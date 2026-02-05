<![CDATA[<div align="center">

# 🌲 CodeTree

### Vectorless RAG for Code Repositories

**Navigate your codebase like a human expert — using LLM reasoning, not vector similarity.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/toller892/Oh-Code-Rag?style=social)](https://github.com/toller892/Oh-Code-Rag)

[Features](#-features) • [Quick Start](#-quick-start) • [Use Cases](#-use-cases) • [How It Works](#-how-it-works) • [Examples](#-real-world-examples)

</div>

---

## 🤔 The Problem

Traditional RAG (Retrieval-Augmented Generation) for code has fundamental limitations:

```
❌ Vector similarity ≠ Code relevance
   "login" and "logout" have similar embeddings, but they're completely different!

❌ Chunking destroys code structure  
   Splitting a class across chunks loses critical context

❌ Can't follow the call chain
   "Who calls this function?" is nearly impossible with vectors

❌ No understanding of code architecture
   Vectors don't know that auth/ is for authentication
```

## 💡 The Solution

**CodeTree** takes a different approach — it builds a hierarchical tree index of your codebase and uses **LLM reasoning** to navigate it, just like a human developer would:

```
✅ AST-based parsing preserves code structure
✅ LLM reasons about which files are relevant  
✅ Understands module relationships and dependencies
✅ Can trace function calls across files
```

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🚫 No Vector Database
Uses code structure + LLM reasoning instead of embedding similarity. No Pinecone, no Milvus, no ChromaDB needed.

### 🌳 AST-Based Indexing  
Parses actual code structure — functions, classes, imports, dependencies. Not just text chunks.

### 🔗 Cross-File Intelligence
Tracks imports, function calls, and dependencies across your entire codebase.

</td>
<td width="50%">

### 🧠 Reasoning-Based Retrieval
LLM navigates the code tree like a human expert, finding relevant code through logical reasoning.

### 💬 Natural Language Queries
Ask questions in plain English: "How does authentication work?" or "Where is the database connection?"

### 🔒 Privacy-First
Works with local models (Ollama). Your code never leaves your machine.

</td>
</tr>
</table>

---

## 📊 Comparison

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

# Index your repository
tree = CodeTree("/path/to/your/repo")
tree.build_index()

# Ask questions about the code
answer = tree.query("How does the authentication system work?")
print(answer)
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

<table>
<tr>
<td>

**Onboarding to New Codebases**
```
Q: "What's the overall architecture of this project?"
Q: "How do requests flow from API to database?"
Q: "Where should I add a new payment method?"
```

</td>
<td>

**Code Review & Understanding**
```
Q: "What does the processOrder function do?"
Q: "Who calls the validateUser method?"
Q: "What happens if authentication fails?"
```

</td>
</tr>
</table>

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

```python
from codetree import CodeTree

tree = CodeTree("./my-project")
tree.build_index()

answer = tree.query("What's the overall architecture? What are the core modules?")
```

**Output:**
```markdown
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

```python
# Find all references to "authenticate"
refs = tree.find("authenticate")
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

```python
answer = tree.query("How does a user login request flow through the system?")
```

**Output:**
```markdown
## Login Request Flow

1. **Entry Point**: `src/api/routes.py`
   ```python
   @app.post("/login")
   def login(credentials: LoginRequest):
       return auth_service.authenticate(credentials)
   ```

2. **Authentication**: `src/auth/service.py`
   - Validates credentials against database
   - Generates JWT token on success
   
3. **Database**: `src/db/users.py`
   - `get_user_by_email()` fetches user record
   - `verify_password()` checks hash

4. **Response**: Returns JWT token or 401 error
```

---

## 🏗️ How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CodeTree                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  CodeParser  │───▶│ CodeIndexer  │───▶│  CodeIndex   │      │
│  │              │    │              │    │  (JSON)      │      │
│  │ • Python     │    │ • Directory  │    │              │      │
│  │ • JavaScript │    │   traversal  │    │ • TreeNodes  │      │
│  │ • Go, Rust   │    │ • AST parse  │    │ • Functions  │      │
│  │ • Java       │    │ • Build tree │    │ • Classes    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                  │               │
│                                                  ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Answer     │◀───│   Retrieve   │◀───│ CodeRetriever│      │
│  │              │    │   Files      │    │              │      │
│  │ • Markdown   │    │              │    │ • LLM Client │      │
│  │ • Code refs  │    │ • Read code  │    │ • Reasoning  │      │
│  │ • Examples   │    │ • Context    │    │ • Navigation │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Two-Stage Retrieval Process

```
Stage 1: Reasoning-Based Navigation
┌─────────────────────────────────────────────────────────────┐
│ User: "How does authentication work?"                        │
│                           │                                  │
│                           ▼                                  │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ LLM analyzes code tree structure:                       │ │
│ │                                                         │ │
│ │ "Authentication relates to auth module...              │ │
│ │  Let me check src/auth/ directory...                   │ │
│ │  login.py and oauth.py look relevant...                │ │
│ │  Also need to check who imports these..."              │ │
│ └─────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ▼                                  │
│ Selected: [src/auth/login.py, src/auth/oauth.py,            │
│            src/middleware/auth.py]                           │
└─────────────────────────────────────────────────────────────┘

Stage 2: Answer Generation  
┌─────────────────────────────────────────────────────────────┐
│ Read selected files → Generate comprehensive answer          │
│ with code snippets and explanations                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗣️ Supported Languages

| Language | Extensions | Parser Status |
|----------|------------|:-------------:|
| Python | `.py`, `.pyi` | ✅ Full |
| JavaScript | `.js`, `.jsx`, `.mjs` | ✅ Full |
| TypeScript | `.ts`, `.tsx` | ✅ Full |
| Go | `.go` | ✅ Full |
| Rust | `.rs` | ✅ Full |
| Java | `.java` | ✅ Full |
| C/C++ | `.c`, `.cpp`, `.h` | 🚧 Coming |

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

| Metric | Small Repo (<100 files) | Medium Repo (<1000 files) | Large Repo (<10000 files) |
|--------|:-----------------------:|:-------------------------:|:-------------------------:|
| Index Time | < 5s | < 30s | < 5min |
| Index Size | < 100KB | < 1MB | < 10MB |
| Query Time | 2-5s | 3-8s | 5-15s |

*Times depend on LLM provider latency*

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

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Inspired by [PageIndex](https://github.com/VectifyAI/PageIndex) — vectorless RAG for documents.

---

<div align="center">

**If you find CodeTree useful, please give us a ⭐!**

[![Star History Chart](https://api.star-history.com/svg?repos=toller892/Oh-Code-Rag&type=Date)](https://star-history.com/#toller892/Oh-Code-Rag&Date)

</div>
]]>