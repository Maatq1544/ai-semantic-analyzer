"""Quick dataset inspection helper.

Usage:
    python scripts/inspect.py path/to/data.csv

Prints row/column counts, empty cells, duplicates, and a 3-row sample.
Useful for the INSPECT stage of the dataset-processor skill.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def inspect(path: Path) -> None:
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        sys.exit(1)

    # Auto-detect format
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path, dtype=str, keep_default_na=False)
    elif suffix == ".json":
        df = pd.read_json(path, dtype=str, convert_dates=False)
    elif suffix in {".jsonl", ".ndjson"}:
        df = pd.read_json(path, lines=True, dtype=str, convert_dates=False)
    elif suffix in {".parquet", ".pq"}:
        df = pd.read_parquet(path).astype(str)
    else:
        print(f"ERROR: unsupported format: {suffix}")
        sys.exit(1)

    print("=" * 60)
    print(f"  Dataset: {path.name}")
    print("=" * 60)
    print(f"Rows:           {len(df)}")
    print(f"Columns:        {len(df.columns)}")
    print(f"Columns list:   {', '.join(df.columns.tolist())}")

    empty_count = int(df.replace("", pd.NA).isna().sum().sum())
    print(f"Empty cells:    {empty_count}")

    duplicate_count = int(df.duplicated().sum())
    print(f"Duplicate rows: {duplicate_count}")

    print()
    print("First 3 rows:")
    print(df.head(3).to_string(max_cols=8, max_colwidth=40))

    # Per-column stats
    print()
    print("Per-column stats:")
    for col in df.columns:
        col_empty = int((df[col] == "").sum())
        col_unique = int(df[col].nunique())
        print(f"  {col:30s}  empty={col_empty:5d}  unique={col_unique:5d}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect.py <path>")
        sys.exit(1)
    inspect(Path(sys.argv[1]))
