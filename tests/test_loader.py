"""Tests for the data loader."""

from pathlib import Path

import pandas as pd
import pytest

from semantic_analyzer.data.loader import DataLoader, detect_format
from semantic_analyzer.exceptions import DataError


def test_detect_format_csv(tmp_path: Path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n")
    assert detect_format(p) == "csv"


def test_detect_format_excel(tmp_path: Path) -> None:
    p = tmp_path / "data.xlsx"
    p.write_text("placeholder")
    assert detect_format(p) == "excel"


def test_detect_format_jsonl(tmp_path: Path) -> None:
    p = tmp_path / "data.jsonl"
    p.write_text('{"a": 1}\n')
    assert detect_format(p) == "jsonl"


def test_detect_format_unknown(tmp_path: Path) -> None:
    p = tmp_path / "data.unknownext"
    p.write_text("data")
    with pytest.raises(DataError):
        detect_format(p)


def test_loader_csv(tmp_path: Path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("name,age\nAlice,30\nBob,25\n")
    loader = DataLoader()
    df = loader.load(p)
    assert len(df) == 2
    assert list(df.columns) == ["name", "age"]
    assert df.iloc[0]["name"] == "Alice"


def test_loader_missing_file(tmp_path: Path) -> None:
    loader = DataLoader()
    with pytest.raises(DataError):
        loader.load(tmp_path / "missing.csv")


def test_loader_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "empty.csv"
    p.write_text("a,b\n")
    loader = DataLoader()
    with pytest.raises(DataError):
        loader.load(p)
