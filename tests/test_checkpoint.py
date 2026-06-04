"""Tests for the checkpoint system."""

import time
from pathlib import Path

from semantic_analyzer.pipeline.checkpoint import Checkpoint, CheckpointStore


def test_save_and_load(tmp_path: Path) -> None:
    store = CheckpointStore(tmp_path)
    ckpt = Checkpoint(
        run_id="test-1",
        input_path="data.csv",
        task_description="sentiment",
        started_at=time.time(),
        last_updated=time.time(),
    )
    store.save(ckpt)

    loaded = store.load("test-1")
    assert loaded is not None
    assert loaded.run_id == "test-1"


def test_load_missing(tmp_path: Path) -> None:
    store = CheckpointStore(tmp_path)
    assert store.load("nonexistent") is None


def test_mark_chunk_done(tmp_path: Path) -> None:
    store = CheckpointStore(tmp_path)
    ckpt = Checkpoint(
        run_id="test-2",
        input_path="data.csv",
        task_description="x",
        started_at=time.time(),
        last_updated=time.time(),
    )
    ckpt.mark_chunk_done(0, [{"a": 1}, {"a": 2}])
    assert ckpt.is_chunk_done(0)
    assert "0:0" in ckpt.chunk_results
    assert "0:1" in ckpt.chunk_results


def test_clear(tmp_path: Path) -> None:
    store = CheckpointStore(tmp_path)
    ckpt = Checkpoint(
        run_id="test-3",
        input_path="x",
        task_description="y",
        started_at=time.time(),
        last_updated=time.time(),
    )
    store.save(ckpt)
    assert store.load("test-3") is not None
    store.clear("test-3")
    assert store.load("test-3") is None


def test_list_runs(tmp_path: Path) -> None:
    store = CheckpointStore(tmp_path)
    for i in range(3):
        store.save(
            Checkpoint(
                run_id=f"r{i}",
                input_path="x",
                task_description="y",
                started_at=time.time(),
                last_updated=time.time(),
            )
        )
    runs = store.list_runs()
    assert "r0" in runs
    assert "r1" in runs
    assert "r2" in runs
