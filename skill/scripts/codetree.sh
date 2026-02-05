#!/bin/bash
# CodeTree CLI wrapper for Clawdbot skill

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODETREE_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Check if codetree is installed
if ! command -v codetree &> /dev/null; then
    # Try to use from source
    if [ -f "$CODETREE_ROOT/src/codetree/cli.py" ]; then
        export PYTHONPATH="$CODETREE_ROOT/src:$PYTHONPATH"
        CODETREE_CMD="python3 -m codetree.cli"
    else
        echo "Error: codetree not installed. Run: pip install -e $CODETREE_ROOT"
        exit 1
    fi
else
    CODETREE_CMD="codetree"
fi

usage() {
    cat << EOF
CodeTree - Vectorless RAG for Code Repositories

Usage: codetree.sh <command> <repo_path> [args...]

Commands:
    index <repo>              Build index for a repository
    query <repo> "<question>" Ask a question about the code
    tree <repo>               Show the code structure
    find <repo> "<symbol>"    Find references to a symbol
    stats <repo>              Show repository statistics
    chat <repo>               Interactive chat mode

Examples:
    codetree.sh index ./my-project
    codetree.sh query ./my-project "How does auth work?"
    codetree.sh find ./my-project "UserService"
EOF
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
    index)
        if [ $# -lt 1 ]; then
            echo "Usage: codetree.sh index <repo_path>"
            exit 1
        fi
        REPO_PATH="$1"
        echo "🌲 Indexing repository: $REPO_PATH"
        $CODETREE_CMD index "$REPO_PATH"
        ;;
    
    query)
        if [ $# -lt 2 ]; then
            echo "Usage: codetree.sh query <repo_path> \"<question>\""
            exit 1
        fi
        REPO_PATH="$1"
        QUESTION="$2"
        $CODETREE_CMD query "$QUESTION" --repo "$REPO_PATH"
        ;;
    
    tree)
        if [ $# -lt 1 ]; then
            echo "Usage: codetree.sh tree <repo_path>"
            exit 1
        fi
        REPO_PATH="$1"
        DEPTH="${2:-3}"
        $CODETREE_CMD tree --repo "$REPO_PATH" --depth "$DEPTH"
        ;;
    
    find)
        if [ $# -lt 2 ]; then
            echo "Usage: codetree.sh find <repo_path> \"<symbol>\""
            exit 1
        fi
        REPO_PATH="$1"
        SYMBOL="$2"
        $CODETREE_CMD find "$SYMBOL" --repo "$REPO_PATH"
        ;;
    
    stats)
        if [ $# -lt 1 ]; then
            echo "Usage: codetree.sh stats <repo_path>"
            exit 1
        fi
        REPO_PATH="$1"
        $CODETREE_CMD stats --repo "$REPO_PATH"
        ;;
    
    chat)
        if [ $# -lt 1 ]; then
            echo "Usage: codetree.sh chat <repo_path>"
            exit 1
        fi
        REPO_PATH="$1"
        $CODETREE_CMD chat --repo "$REPO_PATH"
        ;;
    
    help|--help|-h)
        usage
        ;;
    
    *)
        echo "Unknown command: $COMMAND"
        usage
        exit 1
        ;;
esac
