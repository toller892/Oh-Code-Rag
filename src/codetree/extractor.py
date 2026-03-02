"""Smart code extraction - extract relevant code sections with context."""

import re
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class CodeSection:
    """A section of code with context."""
    content: str
    start_line: int
    end_line: int
    type: str  # "function", "class", "full"
    name: Optional[str] = None


class SmartExtractor:
    """Extract code sections intelligently based on focus."""
    
    def __init__(self, max_lines: int = 200):
        self.max_lines = max_lines
    
    def extract_from_file(
        self,
        file_path: Path,
        focus: Optional[list[str]] = None,
        include_imports: bool = True,
    ) -> Optional[str]:
        """
        Extract relevant code from a file.
        
        Args:
            file_path: Path to the file
            focus: List of function/class names to focus on
            include_imports: Whether to include import statements
            
        Returns:
            Extracted code with context
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IOError):
            return None
        
        lines = content.split("\n")
        
        # If no focus, return truncated full content
        if not focus:
            return self._truncate_content(lines)
        
        # Extract focused sections
        sections = []
        
        # Get imports if requested
        if include_imports:
            import_lines = self._extract_imports(lines)
            if import_lines:
                sections.append(CodeSection(
                    content="\n".join(import_lines),
                    start_line=1,
                    end_line=len(import_lines),
                    type="imports",
                ))
        
        # Extract each focused item
        for item in focus:
            section = self._extract_section(lines, item)
            if section:
                sections.append(section)
        
        # Combine sections
        return self._combine_sections(sections, lines)
    
    def _truncate_content(self, lines: list[str]) -> str:
        """Truncate content to max_lines."""
        if len(lines) <= self.max_lines:
            return "\n".join(lines)
        
        return "\n".join(lines[:self.max_lines]) + f"\n\n... ({len(lines) - self.max_lines} more lines)"
    
    def _extract_imports(self, lines: list[str]) -> list[str]:
        """Extract import statements from the beginning of file."""
        imports = []
        in_docstring = False
        docstring_char = None
        
        for line in lines:
            stripped = line.strip()
            
            # Handle docstrings
            if stripped.startswith('"""') or stripped.startswith("'''"):
                if not in_docstring:
                    in_docstring = True
                    docstring_char = stripped[:3]
                    if stripped.endswith(docstring_char) and len(stripped) > 3:
                        in_docstring = False
                elif stripped.endswith(docstring_char):
                    in_docstring = False
                continue
            
            if in_docstring:
                continue
            
            # Skip comments and empty lines
            if not stripped or stripped.startswith("#"):
                continue
            
            # Check for imports
            if stripped.startswith(("import ", "from ")):
                imports.append(line)
            elif imports:  # Stop after first non-import
                break
        
        return imports
    
    def _extract_section(self, lines: list[str], name: str) -> Optional[CodeSection]:
        """Extract a function or class section."""
        # Try to find function definition
        func_pattern = rf"^\s*def\s+{re.escape(name)}\s*\("
        class_pattern = rf"^\s*class\s+{re.escape(name)}\s*[\(:]"
        
        start_line = None
        is_class = False
        
        for i, line in enumerate(lines):
            if re.match(func_pattern, line):
                start_line = i
                break
            elif re.match(class_pattern, line):
                start_line = i
                is_class = True
                break
        
        if start_line is None:
            return None
        
        # Find end of section (next def/class at same or lower indentation)
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())
        end_line = len(lines)
        
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue
            
            current_indent = len(line) - len(line.lstrip())
            
            # Check for next definition at same or lower indentation
            if current_indent <= start_indent:
                if line.strip().startswith(("def ", "class ")):
                    end_line = i
                    break
        
        # Include docstring and decorators before the definition
        actual_start = start_line
        for i in range(start_line - 1, -1, -1):
            line = lines[i].strip()
            if line.startswith("@") or line.startswith("#"):
                actual_start = i
            elif not line:
                continue
            else:
                break
        
        section_lines = lines[actual_start:end_line]
        
        return CodeSection(
            content="\n".join(section_lines),
            start_line=actual_start + 1,
            end_line=end_line,
            type="class" if is_class else "function",
            name=name,
        )
    
    def _combine_sections(self, sections: list[CodeSection], all_lines: list[str]) -> str:
        """Combine extracted sections into a single string."""
        if not sections:
            return self._truncate_content(all_lines)
        
        parts = []
        total_lines = 0
        
        for section in sections:
            if total_lines + section.content.count("\n") > self.max_lines:
                # Truncate this section
                remaining = self.max_lines - total_lines
                section_lines = section.content.split("\n")
                parts.append("\n".join(section_lines[:remaining]))
                parts.append(f"\n... (truncated, {len(section_lines) - remaining} more lines)")
                break
            
            if section.type == "imports":
                parts.append(section.content)
                parts.append("")  # Empty line after imports
            else:
                parts.append(f"# Line {section.start_line}: {section.type} {section.name or ''}")
                parts.append(section.content)
                parts.append("")  # Empty line between sections
            
            total_lines += section.content.count("\n") + 2
        
        return "\n".join(parts)


def extract_code_smart(
    file_path: Path,
    focus: Optional[list[str]] = None,
    max_lines: int = 200,
    include_imports: bool = True,
) -> Optional[str]:
    """
    Convenience function for smart code extraction.
    
    Args:
        file_path: Path to the file
        focus: List of function/class names to focus on
        max_lines: Maximum lines to return
        include_imports: Whether to include import statements
        
    Returns:
        Extracted code or None if file can't be read
    """
    extractor = SmartExtractor(max_lines=max_lines)
    return extractor.extract_from_file(file_path, focus, include_imports)
