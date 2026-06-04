"""Tests for the data writer."""

from pathlib import Path

import pandas as pd

from semantic_analyzer.data.writer import DataWriter, OutputFormat


def test_write_csv(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    writer = DataWriter()
    out = writer.write(df, tmp_path / "out.csv")
    assert out.exists()
    content = out.read_text()
    assert "a,b" in content
    assert "1,x" in content


def test_write_json(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    writer = DataWriter()
    out = writer.write(df, tmp_path / "out.json", fmt=OutputFormat.JSON)
    assert out.exists()
    text = out.read_text()
    assert text.startswith("[")
    assert "1" in text


def test_write_jsonl(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1, 2]})
    writer = DataWriter()
    out = writer.write(df, tmp_path / "out.jsonl", fmt=OutputFormat.JSONL)
    text = out.read_text()
    assert text.count("\n") == 1
    assert text.startswith("{")


def test_write_infer_format(tmp_path: Path) -> None:
    df = pd.DataFrame({"a": [1]})
    writer = DataWriter()
    out = writer.write(df, tmp_path / "out.jsonl")
    assert out.exists()
