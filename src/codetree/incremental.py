"""Incremental indexing support - only re-index changed files."""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime

from .indexer import TreeNode, CodeIndex


@dataclass
class FileMetadata:
    """Metadata for tracking file changes."""
    path: str
    mtime: float
    size: int
    hash: str
    
    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "mtime": self.mtime,
            "size": self.size,
            "hash": self.hash,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FileMetadata":
        return cls(
            path=data["path"],
            mtime=data["mtime"],
            size=data["size"],
            hash=data["hash"],
        )


@dataclass
class IndexMetadata:
    """Metadata for the entire index."""
    version: str = "0.1.0"
    created_at: str = ""
    updated_at: str = ""
    files: dict[str, FileMetadata] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "files": {k: v.to_dict() for k, v in self.files.items()},
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IndexMetadata":
        return cls(
            version=data.get("version", "0.1.0"),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            files={
                k: FileMetadata.from_dict(v) 
                for k, v in data.get("files", {}).items()
            },
        )


class IncrementalIndexer:
    """Handles incremental indexing logic."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path).resolve()
        self.metadata_path = self.repo_path / ".codetree" / "metadata.json"
        self.metadata: Optional[IndexMetadata] = None
    
    def load_metadata(self) -> IndexMetadata:
        """Load existing metadata or create new."""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.metadata = IndexMetadata.from_dict(data)
                    return self.metadata
            except (json.JSONDecodeError, IOError):
                pass
        
        # Create new metadata
        self.metadata = IndexMetadata(
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        return self.metadata
    
    def save_metadata(self) -> None:
        """Save metadata to disk."""
        if not self.metadata:
            return
        
        self.metadata.updated_at = datetime.now().isoformat()
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata.to_dict(), f, indent=2, ensure_ascii=False)
    
    def get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for change detection."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return ""
    
    def get_file_metadata(self, file_path: Path) -> Optional[FileMetadata]:
        """Get metadata for a file."""
        try:
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(self.repo_path))
            
            return FileMetadata(
                path=relative_path,
                mtime=stat.st_mtime,
                size=stat.st_size,
                hash=self.get_file_hash(file_path),
            )
        except (OSError, ValueError):
            return None
    
    def has_file_changed(self, file_path: Path) -> bool:
        """Check if a file has changed since last index."""
        if not self.metadata:
            self.load_metadata()
        
        relative_path = str(file_path.relative_to(self.repo_path))
        old_meta = self.metadata.files.get(relative_path)
        
        if not old_meta:
            return True  # New file
        
        new_meta = self.get_file_metadata(file_path)
        if not new_meta:
            return True  # Can't read, assume changed
        
        # Quick check: size or mtime changed
        if old_meta.size != new_meta.size or old_meta.mtime != new_meta.mtime:
            # Verify with hash
            return old_meta.hash != new_meta.hash
        
        return False
    
    def update_file_metadata(self, file_path: Path) -> None:
        """Update metadata for a file after indexing."""
        if not self.metadata:
            self.load_metadata()
        
        meta = self.get_file_metadata(file_path)
        if meta:
            self.metadata.files[meta.path] = meta
    
    def remove_file_metadata(self, relative_path: str) -> None:
        """Remove metadata for a deleted file."""
        if not self.metadata:
            self.load_metadata()
        
        if relative_path in self.metadata.files:
            del self.metadata.files[relative_path]
    
    def get_changed_files(self, all_files: list[Path]) -> tuple[list[Path], list[str]]:
        """
        Get lists of changed/new files and deleted files.
        
        Returns:
            (changed_files, deleted_files)
        """
        if not self.metadata:
            self.load_metadata()
        
        changed = []
        for file_path in all_files:
            if self.has_file_changed(file_path):
                changed.append(file_path)
        
        # Find deleted files
        current_paths = {str(f.relative_to(self.repo_path)) for f in all_files}
        deleted = [
            path for path in self.metadata.files.keys()
            if path not in current_paths
        ]
        
        return changed, deleted
