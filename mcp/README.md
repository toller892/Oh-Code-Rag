# CodeTree MCP Server

Model Context Protocol (MCP) server for CodeTree. Enables any MCP-compatible AI assistant to query code repositories using natural language.

## Compatible Clients

- **Claude Desktop** (Anthropic)
- **Cline** (VS Code extension)
- **Continue** (IDE extension)
- Any MCP-compatible client

## Installation

### 1. Install CodeTree

```bash
cd /path/to/Oh-Code-Rag
pip install -e .
```

### 2. Configure Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

On Windows, the config is at: `%APPDATA%\Claude\claude_desktop_config.json`

### 3. Restart Claude Desktop

The CodeTree tools will now be available in Claude.

## Available Tools

| Tool | Description |
|------|-------------|
| `codetree_index` | Index a repository (required before other operations) |
| `codetree_query` | Ask natural language questions about code |
| `codetree_tree` | Show the hierarchical code structure |
| `codetree_find` | Find all references to a symbol |
| `codetree_stats` | Get repository statistics |

## Usage Examples

Once configured, you can ask Claude:

- "Use codetree to index my project at /Users/me/projects/myapp"
- "Query the codebase: how does authentication work?"
- "Show me the code structure"
- "Find all references to UserService"

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key (for GPT models) |
| `ANTHROPIC_API_KEY` | Anthropic API key (alternative) |

## Troubleshooting

### Server not starting

Check that:
1. Python 3.10+ is installed
2. CodeTree is installed (`pip install -e .`)
3. Path in config is correct

### Queries timing out

- LLM queries take 2-10 seconds depending on provider
- Large repos may take longer to index initially

### Permission errors

Make sure `server.py` is executable:
```bash
chmod +x /path/to/Oh-Code-Rag/mcp/server.py
```
