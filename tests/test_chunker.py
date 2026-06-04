"""Tests for the chunker."""

import pandas as pd

from semantic_analyzer.config import ChunkStrategy
from semantic_analyzer.data.chunker import Chunker


def test_chunk_none() -> None:
    df = pd.DataFrame({"a": range(100)})
    chunker = Chunker(ChunkStrategy.NONE, 0)
    chunks = list(chunker.chunks(df))
    assert len(chunks) == 1
    assert len(chunks[0][0]) == 100


def test_chunk_by_rows() -> None:
    df = pd.DataFrame({"a": range(250)})
    chunker = Chunker(ChunkStrategy.ROWS, 100)
    chunks = list(chunker.chunks(df))
    assert len(chunks) == 3
    assert len(chunks[0][0]) == 100
    assert len(chunks[1][0]) == 100
    assert len(chunks[2][0]) == 50


def test_chunk_by_tokens() -> None:
    df = pd.DataFrame({"text": ["a" * 100] * 50})
    chunker = Chunker(ChunkStrategy.TOKENS, 50)  # 50 tokens = 200 chars
    chunks = list(chunker.chunks(df))
    # Each row is 100 chars = 25 tokens, so 2 rows per chunk
    assert len(chunks) > 1
    for c, meta in chunks:
        assert meta.estimated_tokens <= 100  # Allow some slack
