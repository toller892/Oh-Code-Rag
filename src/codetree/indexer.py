"""Code indexer - builds tree structure from repository."""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

from .config import Config, IndexConfig
from .parser import CodeParser, FileInfo, LANGUAGE_EXTENSIONS


@dataclass
class TreeNode:
    """A node in the code tree."""
    name: str
    type: str  # "directory", "file"
    path: str
    summary: Optional[str] = None
    language: Optional[str] = None
    
    # For files
    imports: list[str] = field(default_factory=list)
    functions: list[dict] = field(default_factory=list)
    classes: list[dict] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    line_count: int = 0
    
    # For directories
    children: list["TreeNode"] = field(default_factory=list)
    file_count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        result = {
            "name": self.name,
            "type": self.type,
            "path": self.path,
        }
        
        if self.summary:
            result["summary"] = self.summary
            
        if self.type == "file":
            if self.language:
                result["language"] = self.language
            if self.imports:
                result["imports"] = self.imports
            if self.functions:
                result["functions"] = self.functions
            if self.classes:
                result["classes"] = self.classes
            if self.variables:
                result["variables"] = self.variables
            if self.line_count:
                result["line_count"] = self.line_count
        else:  # directory
            if self.children:
                result["children"] = [c.to_dict() for c in self.children]
            if self.file_count:
                result["file_count"] = self.file_count
                
        return result


@dataclass
class CodeIndex:
    """The complete code index for a repository."""
    root: TreeNode
    repo_path: str
    created_at: str
    version: str = "0.1.0"
    total_files: int = 0
    total_lines: int = 0
    languages: dict[str, int] = field(default_factory=dict)  # language -> file count
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "repo_path": self.repo_path,
            "created_at": self.created_at,
            "total_files": self.total_files,
            "total_lines": self.total_lines,
            "languages": self.languages,
            "root": self.root.to_dict(),
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "CodeIndex":
        """Create CodeIndex from dictionary."""
        def parse_node(node_data: dict) -> TreeNode:
            children = []
            if "children" in node_data:
                children = [parse_node(c) for c in node_data["children"]]
            
            return TreeNode(
                name=node_data["name"],
                type=node_data["type"],
                path=node_data["path"],
                summary=node_data.get("summary"),
                language=node_data.get("language"),
                imports=node_data.get("imports", []),
                functions=node_data.get("functions", []),
                classes=node_data.get("classes", []),
                variables=node_data.get("variables", []),
                line_count=node_data.get("line_count", 0),
                children=children,
                file_count=node_data.get("file_count", 0),
            )
        
        return cls(
            root=parse_node(data["root"]),
            repo_path=data["repo_path"],
            created_at=data["created_at"],
            version=data.get("version", "0.1.0"),
            total_files=data.get("total_files", 0),
            total_lines=data.get("total_lines", 0),
            languages=data.get("languages", {}),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "CodeIndex":
        """Create CodeIndex from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def get_compact_tree(self, max_depth: int = 3) -> str:
        """Get a compact text representation of the tree for LLM context."""
        lines = []
        
        def format_node(node: TreeNode, depth: int = 0, prefix: str = ""):
            if depth > max_depth:
                return
            
            indent = "  " * depth
            
            if node.type == "directory":
                lines.append(f"{indent}{prefix}{node.name}/")
                if node.summary:
                    lines.append(f"{indent}  # {node.summary}")
                for i, child in enumerate(node.children):
                    format_node(child, depth + 1)
            else:
                # File
                lang_tag = f"[{node.language}]" if node.language else ""
                lines.append(f"{indent}{prefix}{node.name} {lang_tag}")
                
                # Show functions and classes
                if node.functions:
                    func_names = [f["name"] for f in node.functions[:5]]
                    more = f" (+{len(node.functions) - 5} more)" if len(node.functions) > 5 else ""
                    lines.append(f"{indent}  → functions: {', '.join(func_names)}{more}")
                
                if node.classes:
                    class_names = [c["name"] for c in node.classes[:5]]
                    lines.append(f"{indent}  → classes: {', '.join(class_names)}")
        
        format_node(self.root)
        return "\n".join(lines)


class CodeIndexer:
    """Build code index from a repository."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.load()
        self.parser = CodeParser()
        self._stats = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
        }
    
    def build_index(self, repo_path: Path) -> CodeIndex:
        """Build a code index from the repository."""
        repo_path = Path(repo_path).resolve()
        
        if not repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
        
        self._stats = {
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
        }
        
        root = self._index_directory(repo_path, repo_path)
        
        return CodeIndex(
            root=root,
            repo_path=str(repo_path),
            created_at=datetime.now().isoformat(),
            total_files=self._stats["total_files"],
            total_lines=self._stats["total_lines"],
            languages=self._stats["languages"],
        )
    
    def _index_directory(self, dir_path: Path, repo_root: Path) -> TreeNode:
        """Recursively index a directory."""
        relative_path = dir_path.relative_to(repo_root)
        
        children = []
        file_count = 0
        
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            entries = []
        
        for entry in entries:
            # Skip excluded patterns
            if self._should_exclude(entry, repo_root):
                continue
            
            if entry.is_dir():
                child_node = self._index_directory(entry, repo_root)
                if child_node.children or child_node.type == "file":
                    children.append(child_node)
                    file_count += child_node.file_count
            elif entry.is_file():
                child_node = self._index_file(entry, repo_root)
                if child_node:
                    children.append(child_node)
                    file_count += 1
        
        return TreeNode(
            name=dir_path.name or str(repo_root.name),
            type="directory",
            path=str(relative_path) if str(relative_path) != "." else "",
            children=children,
            file_count=file_count,
        )
    
    def _index_file(self, file_path: Path, repo_root: Path) -> Optional[TreeNode]:
        """Index a single file."""
        relative_path = file_path.relative_to(repo_root)
        
        # Check file size
        try:
            if file_path.stat().st_size > self.config.index.max_file_size:
                return None
        except OSError:
            return None
        
        # Check if it's a supported language
        language = self.parser.detect_language(file_path)
        if not language:
            return None
        
        if language not in self.config.index.languages:
            return None
        
        # Parse the file
        file_info = self.parser.parse_file(file_path)
        if not file_info:
            return None
        
        # Update stats
        self._stats["total_files"] += 1
        self._stats["total_lines"] += file_info.line_count
        self._stats["languages"][language] = self._stats["languages"].get(language, 0) + 1
        
        return TreeNode(
            name=file_path.name,
            type="file",
            path=str(relative_path),
            language=language,
            imports=file_info.imports[:20],  # Limit imports
            functions=[
                {
                    "name": f.name,
                    "signature": f.signature,
                    "docstring": f.docstring,
                    "line": f.start_line,
                }
                for f in file_info.functions[:50]  # Limit functions
            ],
            classes=[
                {
                    "name": c.name,
                    "signature": c.signature,
                    "docstring": c.docstring,
                    "line": c.start_line,
                }
                for c in file_info.classes[:20]  # Limit classes
            ],
            variables=file_info.variables[:10],
            line_count=file_info.line_count,
        )
    
    def _should_exclude(self, path: Path, repo_root: Path) -> bool:
        """Check if a path should be excluded."""
        name = path.name
        
        # Check exclude patterns
        for pattern in self.config.index.exclude:
            if name == pattern or name.startswith(pattern):
                return True
            if path.match(pattern):
                return True
        
        # Skip hidden files/directories
        if name.startswith(".") and name not in (".github",):
            return True
        
        return False
    
    def save_index(self, index: CodeIndex, output_path: Path) -> None:
        """Save index to a JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(index.to_json())
    
    def load_index(self, index_path: Path) -> CodeIndex:
        """Load index from a JSON file."""
        with open(index_path, "r", encoding="utf-8") as f:
            return CodeIndex.from_json(f.read())
