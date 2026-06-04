"""Click-based CLI for the analyzer."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import click
import yaml
from rich.console import Console
from rich.table import Table

from semantic_analyzer import __version__
from semantic_analyzer.config import Config, OutputFormat, Provider
from semantic_analyzer.data import DataLoader
from semantic_analyzer.exceptions import SemanticAnalyzerError
from semantic_analyzer.prompts.templates import DEFAULT_TASKS
from semantic_analyzer.utils.logging import setup_logging

_console = Console(stderr=True)


def _print_help() -> None:
    _console.print(
        """
[bold blue]AI Semantic Analyzer[/bold blue] — Industrial LLM pipeline for CSV/Excel text analysis

[bold]Quick examples:[/bold]
  semantic-analyzer run input.csv "Extract sentiment and sarcasm" -o output.csv
  semantic-analyzer run input.xlsx "Classify tickets" --provider anthropic --model claude-3-5-haiku
  semantic-analyzer convert input.csv output.json
  semantic-analyzer info input.csv
  semantic-analyzer tasks
""",
    )


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="semantic-analyzer")
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=False, path_type=Path),
    default=None,
    help="Path to YAML config file.",
)
@click.pass_context
def main(ctx: click.Context, config: Path | None) -> None:
    """AI Semantic Analyzer — analyze tabular data with LLMs."""
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    if ctx.invoked_subcommand is None:
        _print_help()
        ctx.exit(0)


@main.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("task")
@click.option("-o", "--output", type=click.Path(path_type=Path), default=None, help="Output file path.")
@click.option(
    "-f",
    "--output-format",
    type=click.Choice([f.value for f in OutputFormat]),
    default=None,
    help="Output format (auto-detected from extension if not set).",
)
@click.option(
    "-p",
    "--provider",
    type=click.Choice([p.value for p in Provider]),
    default=None,
    help="LLM provider.",
)
@click.option("--model", type=str, default=None, help="Model name (provider-specific).")
@click.option(
    "-b",
    "--batch-size",
    type=int,
    default=None,
    help="Max rows processed in parallel within a single call.",
)
@click.option(
    "-w",
    "--max-workers",
    type=int,
    default=None,
    help="Number of parallel worker threads.",
)
@click.option(
    "--chunk-size",
    type=int,
    default=None,
    help="Chunk size (rows or tokens, depending on --chunk-strategy). 0 = no chunking.",
)
@click.option(
    "--chunk-strategy",
    type=click.Choice(["none", "rows", "tokens"]),
    default=None,
    help="Chunking strategy.",
)
@click.option("--timeout", type=int, default=None, help="Per-request timeout in seconds.")
@click.option("--max-retries", type=int, default=None, help="Max retries on transient errors.")
@click.option(
    "--resume/--no-resume",
    default=None,
    help="Resume from checkpoint if one exists for this run.",
)
@click.option(
    "--checkpoint-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Where to store checkpoint files.",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=None,
    help="Load + clean + chunk but do not call the LLM.",
)
@click.option(
    "--no-progress",
    is_flag=True,
    default=False,
    help="Disable the progress bar.",
)
@click.option(
    "--no-clean",
    is_flag=True,
    default=False,
    help="Disable data cleaning (dedupe, normalize).",
)
@click.option(
    "--no-dedupe",
    is_flag=True,
    default=False,
    help="Disable deduplication only.",
)
@click.option(
    "--lowercase",
    is_flag=True,
    default=False,
    help="Lowercase all text columns during cleaning.",
)
@click.option(
    "--fill-na",
    type=str,
    default=None,
    help="Fill NaN values with this string before analysis.",
)
@click.option("-v", "--verbose", is_flag=True, default=False, help="Enable debug logging.")
@click.pass_context
def run(
    ctx: click.Context,
    input_path: Path,
    task: str,
    output: Path | None,
    output_format: str | None,
    provider: str | None,
    model: str | None,
    batch_size: int | None,
    max_workers: int | None,
    chunk_size: int | None,
    chunk_strategy: str | None,
    timeout: int | None,
    max_retries: int | None,
    resume: bool | None,
    checkpoint_dir: Path | None,
    dry_run: bool | None,
    no_progress: bool,
    no_clean: bool,
    no_dedupe: bool,
    lowercase: bool,
    fill_na: str | None,
    verbose: bool,
) -> None:
    """Run semantic analysis on INPUT_PATH using TASK description."""
    overrides: dict[str, Any] = {
        "output_format": output_format,
        "provider": provider,
        "batch_size": batch_size,
        "max_workers": max_workers,
        "chunk_size": chunk_size,
        "chunk_strategy": chunk_strategy,
        "timeout": timeout,
        "max_retries": max_retries,
        "resume": resume,
        "checkpoint_dir": checkpoint_dir,
        "dry_run": dry_run,
    }
    # Strip Nones
    overrides = {k: v for k, v in overrides.items() if v is not None}

    if model and provider:
        overrides[provider] = {"model": model}
    elif model:
        _console.print("[yellow]Warning: --model given without --provider; using default model for current provider.[/yellow]")

    if verbose:
        overrides["log_level"] = "DEBUG"
    overrides["show_progress"] = not no_progress

    # Cleaning options
    clean_overrides: dict[str, Any] = {}
    if no_clean:
        clean_overrides = {
            "drop_duplicates": False,
            "drop_empty_rows": False,
            "normalize_text": False,
            "trim_whitespace": False,
        }
    if no_dedupe:
        clean_overrides["drop_duplicates"] = False
    if lowercase:
        clean_overrides["lowercase_text"] = True
    if fill_na is not None:
        clean_overrides["fill_na"] = fill_na
    if clean_overrides:
        overrides["clean"] = clean_overrides

    config = Config.load(ctx.obj.get("config_path")).with_overrides(**overrides)
    setup_logging(config)

    from semantic_analyzer.pipeline import Pipeline

    pipeline = Pipeline(config)
    try:
        result = pipeline.run(input_path, task, output)
    except SemanticAnalyzerError as exc:
        _console.print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(1)

    sys.exit(0)


@main.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.argument("output_path", type=click.Path(path_type=Path))
@click.option(
    "-f",
    "--output-format",
    type=click.Choice([f.value for f in OutputFormat]),
    default=None,
    help="Output format (auto-detected from extension if not set).",
)
@click.pass_context
def convert(
    ctx: click.Context,
    input_path: Path,
    output_path: Path,
    output_format: str | None,
) -> None:
    """Convert INPUT_PATH to OUTPUT_PATH without running the LLM.

    Useful for CSV→JSON, JSONL→Parquet, etc.
    """
    config = Config.load(ctx.obj.get("config_path"))
    if output_format:
        config = config.with_overrides(output_format=output_format)
    setup_logging(config)

    loader = DataLoader()
    from semantic_analyzer.data import DataWriter

    df = loader.load(input_path)
    writer = DataWriter()
    written = writer.write(df, output_path)
    _console.print(f"[green]✓[/green] Converted {len(df)} rows to {written}")


@main.command()
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def info(ctx: click.Context, input_path: Path) -> None:
    """Print summary statistics about INPUT_PATH."""
    import pandas as pd

    loader = DataLoader()
    df = loader.load(input_path)

    table = Table(title=f"Dataset info: {input_path.name}", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Rows", str(len(df)))
    table.add_row("Columns", str(len(df.columns)))
    table.add_row("Columns list", ", ".join(df.columns.tolist()))

    # Empty cell count
    empty = df.replace("", pd.NA).isna().sum().sum()
    table.add_row("Empty cells", str(int(empty)))

    # Duplicates
    dupes = int(df.duplicated().sum())
    table.add_row("Duplicate rows", str(dupes))

    # Sample
    table.add_section()
    table.add_row("First 3 rows", "")
    sample = df.head(3).to_string(max_cols=5, max_colwidth=30)
    for line in sample.split("\n"):
        table.add_row("", line)

    _console.print(table)


@main.command("tasks")
def list_tasks() -> None:
    """List pre-built task templates."""
    table = Table(title="Pre-built task templates", show_header=True, header_style="bold blue")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Task", style="white")

    for name, desc in DEFAULT_TASKS.items():
        table.add_row(name, desc)
    _console.print(table)


@main.command("init-config")
@click.argument("output_path", type=click.Path(path_type=Path), default=Path("semantic-analyzer.yaml"))
def init_config(output_path: Path) -> None:
    """Generate a starter YAML config file."""
    sample: dict[str, Any] = {
        "provider": "deepseek",
        "output_format": "csv",
        "batch_size": 10,
        "max_workers": 5,
        "chunk_size": 0,
        "chunk_strategy": "none",
        "timeout": 60,
        "max_retries": 3,
        "log_level": "INFO",
        "deepseek": {
            "api_key": "${DEEPSEEK_API_KEY}",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat",
        },
        "clean": {
            "drop_duplicates": True,
            "drop_empty_rows": True,
            "normalize_text": True,
            "trim_whitespace": True,
            "lowercase_text": False,
        },
    }
    output_path.write_text(yaml.safe_dump(sample, sort_keys=False))
    _console.print(f"[green]✓[/green] Wrote sample config to {output_path}")


@main.command("checkpoints")
@click.option(
    "--checkpoint-dir",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Checkpoint directory to inspect.",
)
@click.option("--clear", "run_id", default=None, help="Clear the checkpoint with this run ID.")
def checkpoints(checkpoint_dir: Path | None, run_id: str | None) -> None:
    """List or clear checkpoints."""
    from semantic_analyzer.pipeline import CheckpointStore

    base = checkpoint_dir or Path(".checkpoints")
    store = CheckpointStore(base)

    if run_id:
        store.clear(run_id)
        _console.print(f"[green]✓[/green] Cleared checkpoint {run_id}")
        return

    runs = store.list_runs()
    if not runs:
        _console.print("No checkpoints found.")
        return

    table = Table(title=f"Checkpoints in {base}", show_header=True, header_style="bold blue")
    table.add_column("Run ID", style="cyan")
    table.add_column("Updated", style="white")
    for r in runs:
        ckpt = store.load(r)
        if ckpt:
            from datetime import datetime

            ts = datetime.fromtimestamp(ckpt.last_updated).isoformat()
            table.add_row(r, ts)
    _console.print(table)


# Make `python -m semantic_analyzer` work
if __name__ == "__main__":
    main()  # noqa: F841
