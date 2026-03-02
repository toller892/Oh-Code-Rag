"""Progress tracking and display for indexing operations."""

from typing import Optional, Callable
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
)
from rich.console import Console


class ProgressTracker:
    """Tracks and displays progress for indexing operations."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console()
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None
        self._stats = {
            "files_scanned": 0,
            "files_indexed": 0,
            "files_skipped": 0,
            "total_lines": 0,
        }
    
    def start(self, total: Optional[int] = None, description: str = "Indexing") -> None:
        """Start progress tracking."""
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )
        self._progress.start()
        self._task_id = self._progress.add_task(description, total=total)
    
    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        """Update progress."""
        if self._progress and self._task_id is not None:
            kwargs = {"advance": advance}
            if description:
                kwargs["description"] = description
            self._progress.update(self._task_id, **kwargs)
    
    def set_total(self, total: int) -> None:
        """Set total items after starting."""
        if self._progress and self._task_id is not None:
            self._progress.update(self._task_id, total=total)
    
    def finish(self) -> None:
        """Finish progress tracking."""
        if self._progress:
            self._progress.stop()
            self._progress = None
            self._task_id = None
    
    def log(self, message: str, style: str = "") -> None:
        """Log a message (only if verbose)."""
        if self.verbose:
            self.console.print(message, style=style)
    
    def info(self, message: str) -> None:
        """Log info message."""
        self.log(f"ℹ️  {message}", style="cyan")
    
    def success(self, message: str) -> None:
        """Log success message."""
        self.console.print(f"✅ {message}", style="bold green")
    
    def warning(self, message: str) -> None:
        """Log warning message."""
        self.console.print(f"⚠️  {message}", style="bold yellow")
    
    def error(self, message: str) -> None:
        """Log error message."""
        self.console.print(f"❌ {message}", style="bold red")
    
    def increment_stat(self, key: str, value: int = 1) -> None:
        """Increment a statistic."""
        self._stats[key] = self._stats.get(key, 0) + value
    
    def get_stats(self) -> dict:
        """Get current statistics."""
        return self._stats.copy()
    
    def print_summary(self) -> None:
        """Print indexing summary."""
        self.console.print("\n[bold]📊 Indexing Summary[/bold]")
        self.console.print(f"  Files scanned: {self._stats['files_scanned']}")
        self.console.print(f"  Files indexed: {self._stats['files_indexed']}")
        self.console.print(f"  Files skipped: {self._stats['files_skipped']}")
        self.console.print(f"  Total lines: {self._stats['total_lines']:,}")


class SilentProgressTracker(ProgressTracker):
    """Progress tracker that doesn't display anything."""
    
    def start(self, total: Optional[int] = None, description: str = "Indexing") -> None:
        pass
    
    def update(self, advance: int = 1, description: Optional[str] = None) -> None:
        pass
    
    def finish(self) -> None:
        pass
    
    def log(self, message: str, style: str = "") -> None:
        pass
    
    def print_summary(self) -> None:
        pass
