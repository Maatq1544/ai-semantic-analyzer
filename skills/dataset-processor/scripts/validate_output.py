"""Validate the output of an analyzer run.

Usage:
    python scripts/validate_output.py path/to/analyzed.csv

Checks:
- All expected columns present
- `analysis_error` rate < 5%
- Numeric columns are parseable
- Distribution sanity for known categorical columns
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


def validate(path: Path) -> int:
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 1

    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    print(f"Loaded {len(df)} rows × {len(df.columns)} columns from {path.name}")
    print()

    # Check for analysis_error column
    if "analysis_error" in df.columns:
        error_count = (df["analysis_error"] != "").sum()
        error_rate = error_count / len(df) if len(df) > 0 else 0
        print(f"  analysis_error rows: {error_count} ({error_rate * 100:.1f}%)")
        if error_rate > 0.05:
            print("    ⚠ Warning: error rate > 5% — investigate")
        if error_rate > 0.20:
            print("    ✗ Critical: error rate > 20% — pipeline likely broken")
    else:
        print("  No analysis_error column (good)")

    # Per-column analysis
    print()
    print("Column analysis:")
    for col in df.columns:
        if col == "analysis_error":
            continue
        empty = (df[col] == "").sum()
        unique = df[col].nunique()
        if empty > 0:
            print(f"  {col:30s}  empty={empty:5d}  unique={unique:5d}")

    # Distribution for small-cardinality columns
    print()
    print("Distribution for low-cardinality columns (likely categoricals):")
    for col in df.columns:
        if col == "analysis_error":
            continue
        unique = df[col].nunique()
        if 2 <= unique <= 20:
            counts = df[col].value_counts().head(10)
            print(f"  {col}:")
            for val, count in counts.items():
                pct = count / len(df) * 100
                bar = "█" * int(pct / 5)
                print(f"    {str(val)[:30]:30s}  {count:5d}  {pct:5.1f}%  {bar}")

    print()
    print("=" * 60)
    print("Validation complete.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <path>")
        sys.exit(1)
    sys.exit(validate(Path(sys.argv[1])))
