# CodeTree Skill

Query any code repository using natural language. Built on vectorless RAG - uses LLM reasoning instead of vector similarity.

## Prerequisites

1. CodeTree must be installed:
   ```bash
   cd /path/to/Oh-Code-Rag
   pip install -e .
   ```

2. Set your LLM API key:
   ```bash
   export OPENAI_API_KEY="sk-..."
   # or ANTHROPIC_API_KEY
   ```

## Commands

### Index a Repository

Before querying, you need to index the repository:

```bash
./scripts/codetree.sh index /path/to/repo
```

This creates a `.codetree/index.json` in the repo.

### Query Code

Ask questions about the codebase:

```bash
./scripts/codetree.sh query /path/to/repo "How does authentication work?"
```

### Show Code Tree

Display the structure of the codebase:

```bash
./scripts/codetree.sh tree /path/to/repo
```

### Find Symbol

Find all references to a function, class, or variable:

```bash
./scripts/codetree.sh find /path/to/repo "UserService"
```

### Get Stats

Show repository statistics:

```bash
./scripts/codetree.sh stats /path/to/repo
```

## Usage Examples

### Example 1: Understand a New Project

```bash
# First, index the project
./scripts/codetree.sh index ~/projects/my-app

# Ask about architecture
./scripts/codetree.sh query ~/projects/my-app "What's the overall architecture?"

# Ask about specific functionality
./scripts/codetree.sh query ~/projects/my-app "How does the payment system work?"
```

### Example 2: Code Investigation

```bash
# Find all usages of a function
./scripts/codetree.sh find ~/projects/my-app "processOrder"

# Trace the code flow
./scripts/codetree.sh query ~/projects/my-app "What happens when a user clicks checkout?"
```

### Example 3: Onboarding Help

```bash
# Show the project structure
./scripts/codetree.sh tree ~/projects/my-app

# Get statistics
./scripts/codetree.sh stats ~/projects/my-app

# Ask where to add new features
./scripts/codetree.sh query ~/projects/my-app "Where should I add a new API endpoint?"
```

## Supported Languages

- Python (.py)
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- Go (.go)
- Rust (.rs)
- Java (.java)

## Notes

- The index is saved in `.codetree/index.json` inside each repo
- Re-run `index` after significant code changes
- Query time depends on LLM provider latency (typically 2-10 seconds)
- For large repos, first indexing may take a few minutes
