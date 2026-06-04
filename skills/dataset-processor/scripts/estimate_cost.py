"""Estimate cost for a planned run.

Usage:
    python scripts/estimate_cost.py path/to/data.csv --model deepseek-chat
    python scripts/estimate_cost.py path/to/data.csv --rows 10000 --model gpt-4o-mini

Prints estimated input/output tokens and USD cost for the configured model.
Useful for the EXECUTE stage of the dataset-processor skill.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from semantic_analyzer.utils.cost import PRICING_TABLE


def estimate_for_file(path: Path, model: str) -> tuple[int, int]:
    """Return (estimated_input_tokens, estimated_output_tokens) for a file."""
    import pandas as pd

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path, dtype=str, keep_default_na=False)
    elif suffix in {".jsonl", ".ndjson"}:
        df = pd.read_json(path, lines=True, dtype=str, convert_dates=False)
    elif suffix == ".json":
        df = pd.read_json(path, dtype=str, convert_dates=False)
    else:
        msg = f"unsupported format: {suffix}"
        raise ValueError(msg)

    # Rough estimate: sum of character lengths / 4 ≈ tokens
    total_chars = 0
    for col in df.columns:
        if df[col].dtype == "object":
            total_chars += df[col].astype(str).str.len().sum()

    # Per-row overhead for the system + task prompt (~500 tokens)
    overhead = 500 * len(df)
    input_tokens = overhead + total_chars // 4
    # Output ~150 tokens per row (5 fields × 30 tokens)
    output_tokens = 150 * len(df)
    return input_tokens, output_tokens


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate cost for a run")
    parser.add_argument("path", nargs="?", type=Path, help="Input data file")
    parser.add_argument(
        "--rows",
        type=int,
        default=None,
        help="Estimate for this many rows (skip file inspection)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="deepseek-chat",
        choices=list(PRICING_TABLE.keys()),
        help="LLM model to estimate for",
    )
    args = parser.parse_args()

    if args.rows is not None:
        # Estimate per-row
        per_row_chars = 300  # rough average
        input_tokens = args.rows * (500 + per_row_chars // 4)
        output_tokens = args.rows * 150
    elif args.path:
        input_tokens, output_tokens = estimate_for_file(args.path, args.model)
    else:
        parser.error("either path or --rows is required")

    pricing = PRICING_TABLE.get(args.model)
    if pricing is None:
        print(f"WARNING: model {args.model} not in pricing table — cost unknown")
        cost = None
    else:
        cost = (input_tokens * pricing.input_per_million / 1_000_000) + (
            output_tokens * pricing.output_per_million / 1_000_000
        )

    print(f"Model:              {args.model}")
    print(f"Estimated rows:     {input_tokens // 650:,}")  # rough: 650 tokens per row
    print(f"Input tokens:       {input_tokens:,}")
    print(f"Output tokens:      {output_tokens:,}")
    print(f"Total tokens:       {input_tokens + output_tokens:,}")
    if cost is not None:
        print(f"Estimated cost:     ${cost:.4f} USD")
    print()
    print("Note: This is a rough estimate. Actual cost may vary by 20-30%.")


if __name__ == "__main__":
    main()
