"""Code parser using tree-sitter for AST extraction."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Language file extensions mapping
LANGUAGE_EXTENSIONS = {
    "python": [".py", ".pyi"],
    "javascript": [".js", ".jsx", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "go": [".go"],
    "rust": [".rs"],
    "java": [".java"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".hpp", ".cc", ".cxx"],
}


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, etc.)."""
    name: str
    type: str  # function, class, method, variable
    start_line: int
    end_line: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    decorators: list[str] = field(default_factory=list)
    children: list["CodeEntity"] = field(default_factory=list)


@dataclass
class FileInfo:
    """Parsed information about a code file."""
    path: Path
    language: str
    imports: list[str] = field(default_factory=list)
    functions: list[CodeEntity] = field(default_factory=list)
    classes: list[CodeEntity] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    summary: Optional[str] = None
    line_count: int = 0


class CodeParser:
    """Parse code files to extract structure information."""

    def __init__(self):
        self._parsers = {}

    def detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()
        for lang, extensions in LANGUAGE_EXTENSIONS.items():
            if suffix in extensions:
                return lang
        return None

    def parse_file(self, file_path: Path, content: Optional[str] = None) -> Optional[FileInfo]:
        """Parse a code file and extract structure information."""
        language = self.detect_language(file_path)
        if not language:
            return None

        if content is None:
            try:
                content = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, IOError):
                return None

        lines = content.split("\n")
        
        # Use regex-based parsing for now (simpler than tree-sitter for MVP)
        if language == "python":
            return self._parse_python(file_path, content, lines)
        elif language in ("javascript", "typescript"):
            return self._parse_javascript(file_path, content, lines, language)
        elif language == "go":
            return self._parse_go(file_path, content, lines)
        elif language == "rust":
            return self._parse_rust(file_path, content, lines)
        elif language == "java":
            return self._parse_java(file_path, content, lines)
        else:
            # Basic fallback
            return FileInfo(
                path=file_path,
                language=language,
                line_count=len(lines),
            )

    def _parse_python(self, file_path: Path, content: str, lines: list[str]) -> FileInfo:
        """Parse Python file."""
        imports = []
        functions = []
        classes = []
        variables = []

        # Extract imports
        import_pattern = re.compile(r"^(?:from\s+[\w.]+\s+)?import\s+.+", re.MULTILINE)
        for match in import_pattern.finditer(content):
            imports.append(match.group().strip())

        # Extract functions
        func_pattern = re.compile(
            r"^(?P<decorators>(?:@[\w.]+(?:\([^)]*\))?\s*\n)*)"
            r"(?P<async>async\s+)?def\s+(?P<name>\w+)\s*\((?P<params>[^)]*)\)",
            re.MULTILINE
        )
        for match in func_pattern.finditer(content):
            start_line = content[:match.start()].count("\n") + 1
            name = match.group("name")
            signature = f"def {name}({match.group('params')})"
            if match.group("async"):
                signature = "async " + signature
            
            decorators = []
            if match.group("decorators"):
                decorators = [d.strip() for d in match.group("decorators").strip().split("\n") if d.strip()]
            
            # Find docstring
            docstring = self._extract_python_docstring(content, match.end())
            
            functions.append(CodeEntity(
                name=name,
                type="function",
                start_line=start_line,
                end_line=start_line,  # Simplified
                signature=signature,
                decorators=decorators,
                docstring=docstring,
            ))

        # Extract classes
        class_pattern = re.compile(
            r"^(?P<decorators>(?:@[\w.]+(?:\([^)]*\))?\s*\n)*)"
            r"class\s+(?P<name>\w+)(?:\((?P<bases>[^)]*)\))?:",
            re.MULTILINE
        )
        for match in class_pattern.finditer(content):
            start_line = content[:match.start()].count("\n") + 1
            name = match.group("name")
            bases = match.group("bases") or ""
            
            decorators = []
            if match.group("decorators"):
                decorators = [d.strip() for d in match.group("decorators").strip().split("\n") if d.strip()]
            
            docstring = self._extract_python_docstring(content, match.end())
            
            classes.append(CodeEntity(
                name=name,
                type="class",
                start_line=start_line,
                end_line=start_line,  # Simplified
                signature=f"class {name}({bases})" if bases else f"class {name}",
                decorators=decorators,
                docstring=docstring,
            ))

        # Extract module-level variables (simplified)
        var_pattern = re.compile(r"^([A-Z][A-Z_0-9]*)\s*=", re.MULTILINE)
        for match in var_pattern.finditer(content):
            variables.append(match.group(1))

        return FileInfo(
            path=file_path,
            language="python",
            imports=imports,
            functions=functions,
            classes=classes,
            variables=variables,
            line_count=len(lines),
        )

    def _extract_python_docstring(self, content: str, pos: int) -> Optional[str]:
        """Extract Python docstring after a definition."""
        remaining = content[pos:pos + 500]
        # Look for triple-quoted string
        match = re.search(r'^\s*:\s*\n\s*("""|\'\'\')(.+?)\1', remaining, re.DOTALL)
        if match:
            return match.group(2).strip()[:200]  # Truncate
        return None

    def _parse_javascript(self, file_path: Path, content: str, lines: list[str], language: str) -> FileInfo:
        """Parse JavaScript/TypeScript file."""
        imports = []
        functions = []
        classes = []

        # Extract imports
        import_pattern = re.compile(r"^(?:import|export)\s+.+?['\"];?$", re.MULTILINE)
        for match in import_pattern.finditer(content):
            imports.append(match.group().strip())

        # Extract functions
        func_patterns = [
            # function declaration
            re.compile(r"(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)"),
            # arrow function with const
            re.compile(r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>"),
        ]
        for pattern in func_patterns:
            for match in pattern.finditer(content):
                start_line = content[:match.start()].count("\n") + 1
                name = match.group(1)
                functions.append(CodeEntity(
                    name=name,
                    type="function",
                    start_line=start_line,
                    end_line=start_line,
                ))

        # Extract classes
        class_pattern = re.compile(r"(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?")
        for match in class_pattern.finditer(content):
            start_line = content[:match.start()].count("\n") + 1
            name = match.group(1)
            extends = match.group(2)
            classes.append(CodeEntity(
                name=name,
                type="class",
                start_line=start_line,
                end_line=start_line,
                signature=f"class {name}" + (f" extends {extends}" if extends else ""),
            ))

        return FileInfo(
            path=file_path,
            language=language,
            imports=imports,
            functions=functions,
            classes=classes,
            line_count=len(lines),
        )

    def _parse_go(self, file_path: Path, content: str, lines: list[str]) -> FileInfo:
        """Parse Go file."""
        imports = []
        functions = []

        # Extract imports
        import_pattern = re.compile(r'import\s+(?:\(\s*([^)]+)\s*\)|"([^"]+)")')
        for match in import_pattern.finditer(content):
            if match.group(1):
                for line in match.group(1).strip().split("\n"):
                    line = line.strip().strip('"')
                    if line:
                        imports.append(line)
            elif match.group(2):
                imports.append(match.group(2))

        # Extract functions
        func_pattern = re.compile(r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)")
        for match in func_pattern.finditer(content):
            start_line = content[:match.start()].count("\n") + 1
            name = match.group(1)
            params = match.group(2)
            functions.append(CodeEntity(
                name=name,
                type="function",
                start_line=start_line,
                end_line=start_line,
                signature=f"func {name}({params})",
            ))

        return FileInfo(
            path=file_path,
            language="go",
            imports=imports,
            functions=functions,
            line_count=len(lines),
        )

    def _parse_rust(self, file_path: Path, content: str, lines: list[str]) -> FileInfo:
        """Parse Rust file."""
        imports = []
        functions = []

        # Extract use statements
        use_pattern = re.compile(r"^use\s+.+;", re.MULTILINE)
        for match in use_pattern.finditer(content):
            imports.append(match.group().strip())

        # Extract functions
        func_pattern = re.compile(r"(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*(?:<[^>]+>)?\s*\(([^)]*)\)")
        for match in func_pattern.finditer(content):
            start_line = content[:match.start()].count("\n") + 1
            name = match.group(1)
            functions.append(CodeEntity(
                name=name,
                type="function",
                start_line=start_line,
                end_line=start_line,
            ))

        return FileInfo(
            path=file_path,
            language="rust",
            imports=imports,
            functions=functions,
            line_count=len(lines),
        )

    def _parse_java(self, file_path: Path, content: str, lines: list[str]) -> FileInfo:
        """Parse Java file."""
        imports = []
        functions = []
        classes = []

        # Extract imports
        import_pattern = re.compile(r"^import\s+.+;", re.MULTILINE)
        for match in import_pattern.finditer(content):
            imports.append(match.group().strip())

        # Extract classes
        class_pattern = re.compile(r"(?:public\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?")
        for match in class_pattern.finditer(content):
            start_line = content[:match.start()].count("\n") + 1
            name = match.group(1)
            classes.append(CodeEntity(
                name=name,
                type="class",
                start_line=start_line,
                end_line=start_line,
            ))

        # Extract methods
        method_pattern = re.compile(
            r"(?:public|private|protected)?\s*(?:static\s+)?(?:\w+)\s+(\w+)\s*\(([^)]*)\)"
        )
        for match in method_pattern.finditer(content):
            name = match.group(1)
            if name not in ("if", "while", "for", "switch", "catch"):
                start_line = content[:match.start()].count("\n") + 1
                functions.append(CodeEntity(
                    name=name,
                    type="method",
                    start_line=start_line,
                    end_line=start_line,
                ))

        return FileInfo(
            path=file_path,
            language="java",
            imports=imports,
            functions=functions,
            classes=classes,
            line_count=len(lines),
        )
