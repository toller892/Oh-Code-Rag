"""Command-line interface for CodeTree."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree as RichTree

from .core import CodeTree
from .config import Config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """🌲 CodeTree - Vectorless RAG for Code Repositories"""
    pass


@main.command()
@click.argument("repo_path", type=click.Path(exists=True), default=".")
@click.option("--output", "-o", type=click.Path(), help="Output path for index JSON")
def index(repo_path: str, output: str | None):
    """Build an index for a code repository."""
    repo_path = Path(repo_path).resolve()
    
    console.print(f"\n🌲 [bold]CodeTree[/bold] - Indexing repository...")
    console.print(f"   Path: [cyan]{repo_path}[/cyan]\n")
    
    with console.status("[bold green]Parsing code..."):
        tree = CodeTree(repo_path)
        index = tree.build_index(save=(output is None))
    
    # Print stats
    console.print(Panel.fit(
        f"[green]✓[/green] Indexed [bold]{index.total_files}[/bold] files\n"
        f"[green]✓[/green] [bold]{index.total_lines:,}[/bold] total lines\n"
        f"[green]✓[/green] Languages: {', '.join(index.languages.keys())}",
        title="Index Complete",
        border_style="green",
    ))
    
    if output:
        output_path = Path(output)
        tree.indexer.save_index(index, output_path)
        console.print(f"\n📁 Index saved to: [cyan]{output_path}[/cyan]")
    else:
        console.print(f"\n📁 Index saved to: [cyan]{repo_path / '.codetree' / 'index.json'}[/cyan]")


@main.command()
@click.argument("question")
@click.option("--repo", "-r", type=click.Path(exists=True), default=".", help="Repository path")
def query(question: str, repo: str):
    """Query the codebase with a natural language question."""
    repo_path = Path(repo).resolve()
    
    tree = CodeTree(repo_path)
    
    if tree.index is None:
        console.print("[yellow]No index found. Building index first...[/yellow]\n")
        with console.status("[bold green]Indexing..."):
            tree.build_index()
    
    console.print(f"\n🔍 [bold]Question:[/bold] {question}\n")
    
    with console.status("[bold green]Thinking..."):
        answer = tree.query(question)
    
    console.print(Panel(answer, title="Answer", border_style="blue"))


@main.command()
@click.option("--repo", "-r", type=click.Path(exists=True), default=".", help="Repository path")
def chat(repo: str):
    """Interactive chat mode for querying the codebase."""
    repo_path = Path(repo).resolve()
    
    tree = CodeTree(repo_path)
    
    if tree.index is None:
        console.print("[yellow]No index found. Building index first...[/yellow]\n")
        with console.status("[bold green]Indexing..."):
            tree.build_index()
    
    console.print(Panel.fit(
        "🌲 [bold]CodeTree Interactive Mode[/bold]\n\n"
        f"Repository: [cyan]{repo_path.name}[/cyan]\n"
        f"Files indexed: [green]{tree.index.total_files}[/green]\n\n"
        "Type your questions about the code.\n"
        "Commands: [dim]/tree, /stats, /find <symbol>, /quit[/dim]",
        border_style="green",
    ))
    
    while True:
        try:
            question = console.input("\n[bold cyan]You:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n\n👋 Goodbye!")
            break
        
        if not question:
            continue
        
        if question.lower() in ("/quit", "/exit", "/q"):
            console.print("\n👋 Goodbye!")
            break
        
        if question.lower() == "/tree":
            console.print("\n" + tree.tree(max_depth=3))
            continue
        
        if question.lower() == "/stats":
            stats = tree.stats()
            console.print(Panel.fit(
                f"Files: [bold]{stats['total_files']}[/bold]\n"
                f"Lines: [bold]{stats['total_lines']:,}[/bold]\n"
                f"Languages: {', '.join(f'{k}({v})' for k, v in stats['languages'].items())}",
                title="Repository Stats",
            ))
            continue
        
        if question.lower().startswith("/find "):
            symbol = question[6:].strip()
            refs = tree.find(symbol)
            if refs:
                console.print(f"\n📍 Found [bold]{len(refs)}[/bold] references to '{symbol}':\n")
                for ref in refs[:20]:
                    console.print(f"  • [{ref['type']}] {ref['file']}: {ref.get('name', ref.get('statement', ''))}")
            else:
                console.print(f"\n[yellow]No references found for '{symbol}'[/yellow]")
            continue
        
        # Regular question
        with console.status("[bold green]Thinking..."):
            answer = tree.query(question)
        
        console.print(f"\n[bold green]CodeTree:[/bold green]\n{answer}")


@main.command()
@click.option("--repo", "-r", type=click.Path(exists=True), default=".", help="Repository path")
@click.option("--depth", "-d", type=int, default=3, help="Maximum tree depth")
def tree(repo: str, depth: int):
    """Show the code tree structure."""
    repo_path = Path(repo).resolve()
    
    ct = CodeTree(repo_path)
    
    if ct.index is None:
        console.print("[yellow]No index found. Building index first...[/yellow]\n")
        with console.status("[bold green]Indexing..."):
            ct.build_index()
    
    console.print(f"\n🌲 [bold]Code Tree:[/bold] {repo_path.name}\n")
    console.print(ct.tree(max_depth=depth))


@main.command()
@click.argument("symbol")
@click.option("--repo", "-r", type=click.Path(exists=True), default=".", help="Repository path")
def find(symbol: str, repo: str):
    """Find references to a symbol in the codebase."""
    repo_path = Path(repo).resolve()
    
    ct = CodeTree(repo_path)
    
    if ct.index is None:
        console.print("[yellow]No index found. Building index first...[/yellow]\n")
        with console.status("[bold green]Indexing..."):
            ct.build_index()
    
    refs = ct.find(symbol)
    
    if refs:
        console.print(f"\n📍 Found [bold]{len(refs)}[/bold] references to '[cyan]{symbol}[/cyan]':\n")
        for ref in refs:
            if ref["type"] == "import":
                console.print(f"  [dim]import[/dim]  {ref['file']}: {ref['statement']}")
            else:
                line_info = f":{ref['line']}" if ref.get('line') else ""
                console.print(f"  [dim]{ref['type']:8}[/dim] {ref['file']}{line_info} → {ref['name']}")
    else:
        console.print(f"\n[yellow]No references found for '{symbol}'[/yellow]")


@main.command()
@click.option("--repo", "-r", type=click.Path(exists=True), default=".", help="Repository path")
def stats(repo: str):
    """Show statistics about the indexed repository."""
    repo_path = Path(repo).resolve()
    
    ct = CodeTree(repo_path)
    
    if ct.index is None:
        console.print("[red]No index found. Run 'codetree index' first.[/red]")
        sys.exit(1)
    
    s = ct.stats()
    
    console.print(Panel.fit(
        f"[bold]Repository:[/bold] {repo_path.name}\n"
        f"[bold]Path:[/bold] {s['repo_path']}\n\n"
        f"[bold]Files:[/bold] {s['total_files']}\n"
        f"[bold]Lines:[/bold] {s['total_lines']:,}\n\n"
        f"[bold]Languages:[/bold]\n" + 
        "\n".join(f"  • {lang}: {count} files" for lang, count in s['languages'].items()) +
        f"\n\n[dim]Indexed at: {s['created_at']}[/dim]",
        title="📊 Repository Statistics",
        border_style="blue",
    ))


if __name__ == "__main__":
    main()
