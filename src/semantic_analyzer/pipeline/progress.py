"""Progress reporting via Rich."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

_console = Console(stderr=True)


@contextmanager
def progress_bar(enabled: bool = True) -> Iterator[Progress | None]:
    """Context manager yielding a Rich Progress bar (or None if disabled)."""
    if not enabled:
        yield None
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=_console,
    ) as progress:
        yield progress


def print(message: str, *, style: str | None = None) -> None:
    """Print a message to stderr with optional Rich style."""
    _console.print(message, style=style)


def print_success(message: str) -> None:
    _console.print(f"✓ {message}", style="bold green")


def print_warning(message: str) -> None:
    _console.print(f"⚠ {message}", style="bold yellow")


def print_error(message: str) -> None:
    _console.print(f"✗ {message}", style="bold red")


def print_header(title: str) -> None:
    _console.rule(f"[bold blue]{title}")


def print_summary(stats: dict[str, object]) -> None:
    """Print a key-value summary table."""
    from rich.table import Table

    table = Table(title="Run Summary", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    for key, value in stats.items():
        table.add_row(str(key), str(value))
    _console.print(table)
