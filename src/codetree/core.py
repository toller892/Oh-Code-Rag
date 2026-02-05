"""Core CodeTree class - main entry point."""

from pathlib import Path
from typing import Optional

from .config import Config
from .indexer import CodeIndexer, CodeIndex
from .retriever import CodeRetriever


class CodeTree:
    """
    Main CodeTree class for indexing and querying code repositories.
    
    Example usage:
        tree = CodeTree("/path/to/repo")
        tree.build_index()
        answer = tree.query("How does authentication work?")
    """
    
    def __init__(
        self, 
        repo_path: str | Path,
        config: Optional[Config] = None,
    ):
        """
        Initialize CodeTree for a repository.
        
        Args:
            repo_path: Path to the repository to index
            config: Optional configuration object
        """
        self.repo_path = Path(repo_path).resolve()
        self.config = config or Config.load()
        self.indexer = CodeIndexer(self.config)
        self._index: Optional[CodeIndex] = None
        self._retriever: Optional[CodeRetriever] = None
        
        # Check for existing index
        self._index_path = self._get_index_path()
    
    def _get_index_path(self) -> Path:
        """Get the path where index should be stored."""
        # Store in repo's .codetree directory
        return self.repo_path / ".codetree" / "index.json"
    
    @property
    def index(self) -> Optional[CodeIndex]:
        """Get the current index, loading from disk if available."""
        if self._index is None and self._index_path.exists():
            self._index = self.indexer.load_index(self._index_path)
        return self._index
    
    @property
    def retriever(self) -> CodeRetriever:
        """Get the retriever, initializing if needed."""
        if self._retriever is None:
            if self.index is None:
                raise RuntimeError("No index available. Run build_index() first.")
            self._retriever = CodeRetriever(self.index, self.config)
        return self._retriever
    
    def build_index(self, save: bool = True) -> CodeIndex:
        """
        Build the code index for the repository.
        
        Args:
            save: Whether to save the index to disk
            
        Returns:
            The built CodeIndex
        """
        self._index = self.indexer.build_index(self.repo_path)
        self._retriever = None  # Reset retriever
        
        if save:
            self.indexer.save_index(self._index, self._index_path)
        
        return self._index
    
    def query(self, question: str) -> str:
        """
        Query the codebase with a natural language question.
        
        Args:
            question: The question to ask about the code
            
        Returns:
            Answer based on relevant code sections
        """
        return self.retriever.query(question)
    
    def find(self, symbol: str) -> list[dict]:
        """
        Find all occurrences of a symbol in the codebase.
        
        Args:
            symbol: Symbol name to search for (function, class, etc.)
            
        Returns:
            List of references found
        """
        if self.index is None:
            raise RuntimeError("No index available. Run build_index() first.")
        return self._find_references(symbol)
    
    def _find_references(self, symbol: str) -> list[dict]:
        """Find all references to a symbol across the codebase (no LLM needed)."""
        from .indexer import TreeNode
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
    
    def tree(self, max_depth: int = 3) -> str:
        """
        Get a text representation of the code tree.
        
        Args:
            max_depth: Maximum depth to display
            
        Returns:
            Tree structure as string
        """
        if self.index is None:
            raise RuntimeError("No index available. Run build_index() first.")
        return self.index.get_compact_tree(max_depth)
    
    def stats(self) -> dict:
        """
        Get statistics about the indexed repository.
        
        Returns:
            Dictionary with stats (files, lines, languages, etc.)
        """
        if self.index is None:
            raise RuntimeError("No index available. Run build_index() first.")
        
        return {
            "repo_path": self.index.repo_path,
            "total_files": self.index.total_files,
            "total_lines": self.index.total_lines,
            "languages": self.index.languages,
            "created_at": self.index.created_at,
        }
