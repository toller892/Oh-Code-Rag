#!/usr/bin/env python3
"""Test script for the three optimizations."""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from codetree import CodeTree


def test_progress_bar():
    """Test 1: Progress bar during indexing."""
    print("\n" + "="*60)
    print("TEST 1: Progress Bar")
    print("="*60)
    
    # Use the codetree-dev repo itself as test
    repo_path = Path(__file__).parent
    
    tree = CodeTree(repo_path, verbose=True)
    
    print("\n🔄 Building index with progress bar...")
    start = time.time()
    tree.build_index(incremental=False, show_progress=True)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Time taken: {elapsed:.2f}s")
    
    stats = tree.stats()
    print(f"\n📊 Stats:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total lines: {stats['total_lines']:,}")
    print(f"  Languages: {stats['languages']}")
    
    return tree


def test_incremental_indexing(tree):
    """Test 2: Incremental indexing."""
    print("\n" + "="*60)
    print("TEST 2: Incremental Indexing")
    print("="*60)
    
    print("\n🔄 First update (no changes expected)...")
    start = time.time()
    tree.update_index(show_progress=True)
    elapsed = time.time() - start
    print(f"⏱️  Time taken: {elapsed:.2f}s")
    
    # Create a test file
    test_file = tree.repo_path / "test_temp.py"
    print(f"\n📝 Creating test file: {test_file.name}")
    test_file.write_text("""
def test_function():
    '''Test function for incremental indexing.'''
    return "Hello, World!"

class TestClass:
    '''Test class.'''
    def method(self):
        pass
""")
    
    print("\n🔄 Second update (should detect 1 new file)...")
    start = time.time()
    tree.update_index(show_progress=True)
    elapsed = time.time() - start
    print(f"⏱️  Time taken: {elapsed:.2f}s")
    
    # Clean up
    test_file.unlink()
    print(f"\n🗑️  Cleaned up test file")
    
    print("\n🔄 Third update (should detect 1 deleted file)...")
    start = time.time()
    tree.update_index(show_progress=True)
    elapsed = time.time() - start
    print(f"⏱️  Time taken: {elapsed:.2f}s")


def test_smart_extraction(tree):
    """Test 3: Smart code extraction."""
    print("\n" + "="*60)
    print("TEST 3: Smart Code Extraction")
    print("="*60)
    
    # Find a Python file to test
    test_file = tree.repo_path / "src" / "codetree" / "core.py"
    
    if not test_file.exists():
        print("⚠️  Test file not found, skipping...")
        return
    
    print(f"\n📄 Testing extraction from: {test_file.relative_to(tree.repo_path)}")
    
    # Test 1: Full file (truncated)
    print("\n--- Test 3a: Full file (no focus) ---")
    from codetree.extractor import extract_code_smart
    
    content = extract_code_smart(test_file, focus=None, max_lines=50)
    lines = content.split("\n")
    print(f"Extracted {len(lines)} lines")
    print("First 10 lines:")
    print("\n".join(lines[:10]))
    
    # Test 2: Focused extraction
    print("\n--- Test 3b: Focused extraction (CodeTree class) ---")
    content = extract_code_smart(test_file, focus=["CodeTree"], max_lines=100)
    lines = content.split("\n")
    print(f"Extracted {len(lines)} lines")
    print("First 20 lines:")
    print("\n".join(lines[:20]))
    
    # Test 3: Multiple focuses
    print("\n--- Test 3c: Multiple focuses (build_index, update_index) ---")
    content = extract_code_smart(test_file, focus=["build_index", "update_index"], max_lines=150)
    lines = content.split("\n")
    print(f"Extracted {len(lines)} lines")
    print("Sample (lines 1-15):")
    print("\n".join(lines[:15]))


def main():
    """Run all tests."""
    print("\n🚀 CodeTree Optimization Tests")
    print("="*60)
    
    try:
        # Test 1: Progress bar
        tree = test_progress_bar()
        
        # Test 2: Incremental indexing
        test_incremental_indexing(tree)
        
        # Test 3: Smart extraction
        test_smart_extraction(tree)
        
        print("\n" + "="*60)
        print("✅ All tests completed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
