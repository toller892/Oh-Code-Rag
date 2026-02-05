#!/usr/bin/env python3
"""Basic usage example for CodeTree."""

from codetree import CodeTree

# Initialize with a repository path
tree = CodeTree(".")

# Build the index (this will parse all code files)
print("Building index...")
index = tree.build_index()

# Print some stats
print(f"\nIndexed {index.total_files} files")
print(f"Total lines: {index.total_lines:,}")
print(f"Languages: {', '.join(index.languages.keys())}")

# Show the code tree
print("\n--- Code Tree ---")
print(tree.tree(max_depth=2))

# Query the codebase (requires API key)
# answer = tree.query("What does the main function do?")
# print(answer)
