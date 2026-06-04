"""Tests for the data cleaner."""

import pandas as pd

from semantic_analyzer.config import CleanConfig
from semantic_analyzer.data.cleaner import DataCleaner


def test_drop_duplicates() -> None:
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    cleaner = DataCleaner(CleanConfig(drop_duplicates=True))
    out, stats = cleaner.clean(df)
    assert len(out) == 2
    assert stats["dropped_duplicates"] == 1


def test_drop_empty_rows() -> None:
    df = pd.DataFrame({"a": [1, "", ""], "b": ["x", "", ""]})
    cleaner = DataCleaner(CleanConfig(drop_empty_rows=True, drop_duplicates=False, normalize_text=False))
    out, stats = cleaner.clean(df)
    assert len(out) == 1
    assert stats["dropped_empty_rows"] == 2


def test_normalize_text() -> None:
    df = pd.DataFrame({"text": ["  hello   world  ", "test\ttab"]})
    cleaner = DataCleaner(CleanConfig(normalize_text=True, trim_whitespace=True, drop_duplicates=False))
    out, _ = cleaner.clean(df)
    assert out.iloc[0]["text"] == "hello world"
    assert out.iloc[1]["text"] == "test tab"


def test_dedupe_subset() -> None:
    df = pd.DataFrame({"email": ["a@x.com", "a@x.com", "b@x.com"], "name": ["Alice", "Alice2", "Bob"]})
    cleaner = DataCleaner(CleanConfig(dedupe_subset=["email"]))
    out, stats = cleaner.clean(df)
    assert len(out) == 2
    assert stats["dropped_duplicates"] == 1


def test_lowercase() -> None:
    df = pd.DataFrame({"a": ["HELLO", "World"]})
    cleaner = DataCleaner(CleanConfig(lowercase_text=True, normalize_text=True, drop_duplicates=False))
    out = cleaner.apply_lowercase(cleaner.clean(df)[0])
    assert out.iloc[0]["a"] == "hello"


def test_fill_na() -> None:
    df = pd.DataFrame({"a": ["x", ""]})
    cleaner = DataCleaner(CleanConfig(fill_na="MISSING", normalize_text=False, drop_duplicates=False, drop_empty_rows=False))
    out, _ = cleaner.clean(df)
    # Note: cleaner already normalizes "" to "MISSING" via fill_na
    assert "MISSING" in out["a"].values
