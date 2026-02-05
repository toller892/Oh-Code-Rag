"""Reasoning-based code retriever."""

import json
from pathlib import Path
from typing import Optional

from .config import Config
from .indexer import CodeIndex, TreeNode
from .llm import create_llm_client, LLMClient


RETRIEVAL_SYSTEM_PROMPT = """You are a code navigation expert. Your task is to analyze a code repository structure and identify the most relevant files and code sections to answer a user's question.

You will be given:
1. A tree structure of the codebase showing directories, files, functions, and classes
2. A user's question about the code

Your job is to:
1. Analyze the question to understand what the user is looking for
2. Navigate the tree structure using your reasoning
3. Identify the most relevant files and specific functions/classes
4. Return a JSON list of file paths that should be examined

Think step by step:
- What concepts does the question involve? (authentication, database, API, etc.)
- Which directories/modules are likely to contain relevant code?
- Which specific files have functions or classes related to the question?

Return your answer as JSON in this format:
{
  "reasoning": "Brief explanation of your navigation logic",
  "relevant_files": [
    {"path": "path/to/file.py", "relevance": "why this file is relevant", "focus": ["function_name", "ClassName"]}
  ]
}

Only include files that are truly relevant. Aim for 1-5 files maximum."""


ANSWER_SYSTEM_PROMPT = """You are a helpful code assistant. You have been given relevant code sections from a repository to answer a user's question.

Guidelines:
- Answer the question directly and concisely
- Reference specific code sections when relevant
- Include code snippets if they help explain the answer
- If the provided code doesn't fully answer the question, say so
- Use markdown formatting for code blocks"""


class CodeRetriever:
    """Retrieves relevant code using LLM reasoning."""
    
    def __init__(self, index: CodeIndex, config: Optional[Config] = None):
        self.index = index
        self.config = config or Config.load()
        self.llm = create_llm_client(self.config.llm)
        self.repo_path = Path(index.repo_path)
    
    def retrieve(self, query: str, max_files: int = 5) -> list[dict]:
        """Retrieve relevant files for a query using LLM reasoning."""
        # Get compact tree representation
        tree_str = self.index.get_compact_tree(max_depth=4)
        
        # Ask LLM to identify relevant files
        messages = [
            {"role": "system", "content": RETRIEVAL_SYSTEM_PROMPT},
            {"role": "user", "content": f"""## Repository Structure

{tree_str}

## Question
{query}

Analyze the repository structure and identify the most relevant files to answer this question. Return JSON."""}
        ]
        
        response = self.llm.chat(messages)
        
        # Parse response
        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response[json_start:json_end])
                return result.get("relevant_files", [])[:max_files]
        except json.JSONDecodeError:
            pass
        
        return []
    
    def get_file_content(self, file_path: str, focus: Optional[list[str]] = None) -> Optional[str]:
        """Get content of a file, optionally focusing on specific functions/classes."""
        full_path = self.repo_path / file_path
        
        if not full_path.exists():
            return None
        
        try:
            content = full_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IOError):
            return None
        
        # If no focus specified, return full content (truncated)
        if not focus:
            lines = content.split("\n")
            if len(lines) > 200:
                return "\n".join(lines[:200]) + f"\n\n... ({len(lines) - 200} more lines)"
            return content
        
        # TODO: Extract only focused sections
        # For now, return full content
        return content
    
    def query(self, question: str) -> str:
        """Query the codebase and get an answer."""
        # Step 1: Retrieve relevant files
        relevant_files = self.retrieve(question)
        
        if not relevant_files:
            return "I couldn't identify any relevant files for your question. Please try rephrasing or being more specific."
        
        # Step 2: Get file contents
        context_parts = []
        for file_info in relevant_files:
            path = file_info.get("path", "")
            focus = file_info.get("focus", [])
            
            content = self.get_file_content(path, focus)
            if content:
                context_parts.append(f"## File: {path}\n\n```\n{content}\n```")
        
        if not context_parts:
            return "I found relevant files but couldn't read their contents."
        
        # Step 3: Generate answer
        context = "\n\n".join(context_parts)
        
        messages = [
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": f"""## Relevant Code

{context}

## Question
{question}

Please answer the question based on the code provided above."""}
        ]
        
        return self.llm.chat(messages)
    
    def find_references(self, symbol: str) -> list[dict]:
        """Find all references to a symbol across the codebase."""
        references = []
        
        def search_node(node: TreeNode):
            if node.type == "file":
                # Check functions
                for func in node.functions:
                    if symbol.lower() in func.get("name", "").lower():
                        references.append({
                            "type": "function",
                            "file": node.path,
                            "name": func["name"],
                            "line": func.get("line"),
                        })
                
                # Check classes
                for cls in node.classes:
                    if symbol.lower() in cls.get("name", "").lower():
                        references.append({
                            "type": "class",
                            "file": node.path,
                            "name": cls["name"],
                            "line": cls.get("line"),
                        })
                
                # Check imports
                for imp in node.imports:
                    if symbol.lower() in imp.lower():
                        references.append({
                            "type": "import",
                            "file": node.path,
                            "statement": imp,
                        })
            else:
                for child in node.children:
                    search_node(child)
        
        search_node(self.index.root)
        return references
