#!/usr/bin/env python3
"""
CodeTree MCP Server

Model Context Protocol server for CodeTree - enables any MCP-compatible
AI assistant (Claude Desktop, etc.) to query code repositories.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Any, Optional

# MCP Protocol Implementation
class MCPServer:
    """Simple MCP Server implementation for CodeTree."""
    
    def __init__(self):
        self.codetree_instances = {}  # repo_path -> CodeTree instance
        
    async def handle_request(self, request: dict) -> dict:
        """Handle incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list()
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "shutdown":
                result = {}
            else:
                return self.error_response(request_id, -32601, f"Unknown method: {method}")
            
            return self.success_response(request_id, result)
        except Exception as e:
            return self.error_response(request_id, -32603, str(e))
    
    async def handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "codetree-mcp",
                "version": "0.1.0"
            }
        }
    
    async def handle_tools_list(self) -> dict:
        """Return list of available tools."""
        return {
            "tools": [
                {
                    "name": "codetree_index",
                    "description": "Index a code repository for querying. Must be called before other operations on a new repo.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Absolute path to the repository to index"
                            }
                        },
                        "required": ["repo_path"]
                    }
                },
                {
                    "name": "codetree_query",
                    "description": "Ask a natural language question about a code repository. The repo must be indexed first.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Absolute path to the repository"
                            },
                            "question": {
                                "type": "string",
                                "description": "Natural language question about the code"
                            }
                        },
                        "required": ["repo_path", "question"]
                    }
                },
                {
                    "name": "codetree_tree",
                    "description": "Show the hierarchical structure of a code repository.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Absolute path to the repository"
                            },
                            "max_depth": {
                                "type": "integer",
                                "description": "Maximum depth to display (default: 3)",
                                "default": 3
                            }
                        },
                        "required": ["repo_path"]
                    }
                },
                {
                    "name": "codetree_find",
                    "description": "Find all references to a symbol (function, class, variable) in the codebase.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Absolute path to the repository"
                            },
                            "symbol": {
                                "type": "string",
                                "description": "Symbol name to search for"
                            }
                        },
                        "required": ["repo_path", "symbol"]
                    }
                },
                {
                    "name": "codetree_stats",
                    "description": "Get statistics about an indexed repository.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "repo_path": {
                                "type": "string",
                                "description": "Absolute path to the repository"
                            }
                        },
                        "required": ["repo_path"]
                    }
                }
            ]
        }
    
    async def handle_tools_call(self, params: dict) -> dict:
        """Handle tool invocation."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        # Lazy import to avoid startup overhead
        from codetree import CodeTree
        
        repo_path = arguments.get("repo_path", "")
        
        if tool_name == "codetree_index":
            return await self.tool_index(repo_path)
        elif tool_name == "codetree_query":
            question = arguments.get("question", "")
            return await self.tool_query(repo_path, question)
        elif tool_name == "codetree_tree":
            max_depth = arguments.get("max_depth", 3)
            return await self.tool_tree(repo_path, max_depth)
        elif tool_name == "codetree_find":
            symbol = arguments.get("symbol", "")
            return await self.tool_find(repo_path, symbol)
        elif tool_name == "codetree_stats":
            return await self.tool_stats(repo_path)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def get_codetree(self, repo_path: str):
        """Get or create CodeTree instance for a repo."""
        from codetree import CodeTree
        
        repo_path = str(Path(repo_path).resolve())
        
        if repo_path not in self.codetree_instances:
            self.codetree_instances[repo_path] = CodeTree(repo_path)
        
        return self.codetree_instances[repo_path]
    
    async def tool_index(self, repo_path: str) -> dict:
        """Index a repository."""
        tree = self.get_codetree(repo_path)
        index = tree.build_index()
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"✅ Indexed repository: {repo_path}\n\n"
                           f"- Files: {index.total_files}\n"
                           f"- Lines: {index.total_lines:,}\n"
                           f"- Languages: {', '.join(index.languages.keys())}"
                }
            ]
        }
    
    async def tool_query(self, repo_path: str, question: str) -> dict:
        """Query a repository."""
        tree = self.get_codetree(repo_path)
        
        # Auto-index if needed
        if tree.index is None:
            tree.build_index()
        
        answer = tree.query(question)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": answer
                }
            ]
        }
    
    async def tool_tree(self, repo_path: str, max_depth: int = 3) -> dict:
        """Show repository tree."""
        tree = self.get_codetree(repo_path)
        
        if tree.index is None:
            tree.build_index()
        
        tree_str = tree.tree(max_depth=max_depth)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"🌲 Code Tree: {Path(repo_path).name}\n\n{tree_str}"
                }
            ]
        }
    
    async def tool_find(self, repo_path: str, symbol: str) -> dict:
        """Find symbol references."""
        tree = self.get_codetree(repo_path)
        
        if tree.index is None:
            tree.build_index()
        
        refs = tree.find(symbol)
        
        if not refs:
            text = f"No references found for '{symbol}'"
        else:
            lines = [f"📍 Found {len(refs)} references to '{symbol}':\n"]
            for ref in refs:
                if ref["type"] == "import":
                    lines.append(f"  [import]   {ref['file']}: {ref['statement']}")
                else:
                    line_info = f":{ref['line']}" if ref.get('line') else ""
                    lines.append(f"  [{ref['type']:8}] {ref['file']}{line_info} → {ref['name']}")
            text = "\n".join(lines)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    
    async def tool_stats(self, repo_path: str) -> dict:
        """Get repository stats."""
        tree = self.get_codetree(repo_path)
        
        if tree.index is None:
            tree.build_index()
        
        stats = tree.stats()
        
        lang_lines = "\n".join(f"  - {lang}: {count} files" 
                               for lang, count in stats['languages'].items())
        
        text = (f"📊 Repository Statistics\n\n"
                f"Path: {stats['repo_path']}\n"
                f"Files: {stats['total_files']}\n"
                f"Lines: {stats['total_lines']:,}\n\n"
                f"Languages:\n{lang_lines}")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    
    def success_response(self, request_id: Any, result: dict) -> dict:
        """Create success response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def error_response(self, request_id: Any, code: int, message: str) -> dict:
        """Create error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


async def main():
    """Main entry point - runs MCP server over stdio."""
    server = MCPServer()
    
    # Read from stdin, write to stdout
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
    
    writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
        asyncio.streams.FlowControlMixin, sys.stdout
    )
    writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, asyncio.get_event_loop())
    
    while True:
        try:
            # Read Content-Length header
            header = await reader.readline()
            if not header:
                break
            
            # Skip empty lines
            if header.strip() == b"":
                continue
                
            if header.startswith(b"Content-Length:"):
                content_length = int(header.decode().split(":")[1].strip())
                
                # Read empty line after header
                await reader.readline()
                
                # Read content
                content = await reader.read(content_length)
                request = json.loads(content.decode())
                
                # Handle request
                response = await server.handle_request(request)
                
                # Send response
                response_bytes = json.dumps(response).encode()
                writer.write(f"Content-Length: {len(response_bytes)}\r\n\r\n".encode())
                writer.write(response_bytes)
                await writer.drain()
                
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            break


if __name__ == "__main__":
    asyncio.run(main())
