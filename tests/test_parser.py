"""Tests for the code parser."""

import pytest
from pathlib import Path
from codetree.parser import CodeParser, LANGUAGE_EXTENSIONS


class TestCodeParser:
    """Tests for CodeParser class."""
    
    def setup_method(self):
        self.parser = CodeParser()
    
    def test_detect_python(self):
        assert self.parser.detect_language(Path("test.py")) == "python"
        assert self.parser.detect_language(Path("test.pyi")) == "python"
    
    def test_detect_javascript(self):
        assert self.parser.detect_language(Path("test.js")) == "javascript"
        assert self.parser.detect_language(Path("test.jsx")) == "javascript"
        assert self.parser.detect_language(Path("test.mjs")) == "javascript"
    
    def test_detect_typescript(self):
        assert self.parser.detect_language(Path("test.ts")) == "typescript"
        assert self.parser.detect_language(Path("test.tsx")) == "typescript"
    
    def test_detect_unknown(self):
        assert self.parser.detect_language(Path("test.xyz")) is None
        assert self.parser.detect_language(Path("test.md")) is None
    
    def test_parse_python_functions(self):
        content = '''
def hello():
    """Say hello."""
    pass

async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    pass

@decorator
def decorated():
    pass
'''
        result = self.parser._parse_python(Path("test.py"), content, content.split("\n"))
        
        assert len(result.functions) == 3
        assert result.functions[0].name == "hello"
        assert result.functions[1].name == "fetch_data"
        assert result.functions[2].name == "decorated"
    
    def test_parse_python_classes(self):
        content = '''
class MyClass:
    """A simple class."""
    pass

class ChildClass(ParentClass):
    pass

@dataclass
class DataClass:
    pass
'''
        result = self.parser._parse_python(Path("test.py"), content, content.split("\n"))
        
        assert len(result.classes) == 3
        assert result.classes[0].name == "MyClass"
        assert result.classes[1].name == "ChildClass"
        assert result.classes[2].name == "DataClass"
    
    def test_parse_python_imports(self):
        content = '''
import os
import sys
from pathlib import Path
from typing import Optional, List
'''
        result = self.parser._parse_python(Path("test.py"), content, content.split("\n"))
        
        assert len(result.imports) == 4
        assert "import os" in result.imports
        assert "from pathlib import Path" in result.imports


class TestLanguageExtensions:
    """Tests for language extension mappings."""
    
    def test_all_languages_have_extensions(self):
        expected_languages = ["python", "javascript", "typescript", "go", "rust", "java"]
        for lang in expected_languages:
            assert lang in LANGUAGE_EXTENSIONS
            assert len(LANGUAGE_EXTENSIONS[lang]) > 0
