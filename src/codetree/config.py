"""Configuration management for CodeTree."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import yaml


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096

    def __post_init__(self):
        # Resolve environment variables
        if self.api_key and self.api_key.startswith("${") and self.api_key.endswith("}"):
            env_var = self.api_key[2:-1]
            self.api_key = os.environ.get(env_var)
        
        # Try default env vars if no key set
        if not self.api_key:
            if self.provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
            elif self.provider == "anthropic":
                self.api_key = os.environ.get("ANTHROPIC_API_KEY")


@dataclass
class IndexConfig:
    """Index configuration."""
    languages: list[str] = field(default_factory=lambda: ["python", "javascript", "typescript", "go", "rust", "java"])
    exclude: list[str] = field(default_factory=lambda: [
        "node_modules", "__pycache__", ".git", ".venv", "venv", 
        "dist", "build", ".egg-info", ".tox", ".pytest_cache"
    ])
    include_patterns: list[str] = field(default_factory=list)
    max_file_size: int = 100_000  # bytes
    max_files: int = 10_000


@dataclass 
class Config:
    """Main configuration class."""
    llm: LLMConfig = field(default_factory=LLMConfig)
    index: IndexConfig = field(default_factory=IndexConfig)
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "codetree")

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from file or defaults."""
        config = cls()
        
        # Search for config file
        search_paths = []
        if config_path:
            search_paths.append(config_path)
        search_paths.extend([
            Path.cwd() / ".codetree.yaml",
            Path.cwd() / ".codetree.yml",
            Path.home() / ".config" / "codetree" / "config.yaml",
        ])
        
        for path in search_paths:
            if path.exists():
                config = cls.from_yaml(path)
                break
        
        return config

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        
        llm_data = data.get("llm", {})
        index_data = data.get("index", {})
        
        return cls(
            llm=LLMConfig(**llm_data),
            index=IndexConfig(**index_data),
            cache_dir=Path(data.get("cache_dir", Path.home() / ".cache" / "codetree")),
        )

    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file."""
        data = {
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
            },
            "index": {
                "languages": self.index.languages,
                "exclude": self.index.exclude,
                "max_file_size": self.index.max_file_size,
            },
            "cache_dir": str(self.cache_dir),
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
