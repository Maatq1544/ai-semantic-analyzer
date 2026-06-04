"""Checkpoint system for resumable pipelines."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from semantic_analyzer.exceptions import CheckpointError


@dataclass
class Checkpoint:
    """Pipeline state for a single dataset run."""

    run_id: str
    input_path: str
    task_description: str
    started_at: float
    last_updated: float
    completed_chunk_ids: list[int] = field(default_factory=list)
    chunk_results: dict[str, dict[str, Any]] = field(default_factory=dict)
    total_rows: int = 0
    total_chunks: int = 0
    config_snapshot: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Checkpoint:
        return cls(**data)

    def is_chunk_done(self, chunk_id: int) -> bool:
        return chunk_id in self.completed_chunk_ids

    def mark_chunk_done(self, chunk_id: int, results: list[dict[str, Any]]) -> None:
        if chunk_id not in self.completed_chunk_ids:
            self.completed_chunk_ids.append(chunk_id)
        for idx, result in enumerate(results):
            self.chunk_results[f"{chunk_id}:{idx}"] = result
        self.last_updated = time.time()


class CheckpointStore:
    """Persist checkpoints to disk as JSON."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, run_id: str) -> Path:
        return self.base_dir / f"{run_id}.json"

    def save(self, checkpoint: Checkpoint) -> Path:
        """Atomically write the checkpoint to disk.

        Uses a ``.tmp`` file + ``os.replace`` for atomicity.
        """
        path = self._path_for(checkpoint.run_id)
        tmp = path.with_suffix(".tmp")
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(checkpoint.to_dict(), f, indent=2, ensure_ascii=False)
            tmp.replace(path)
        except Exception as exc:
            raise CheckpointError(f"Failed to save checkpoint to {path}: {exc}") from exc
        return path

    def load(self, run_id: str) -> Checkpoint | None:
        """Load a checkpoint, or return None if it doesn't exist."""
        path = self._path_for(run_id)
        if not path.exists():
            return None
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return Checkpoint.from_dict(data)
        except Exception as exc:
            raise CheckpointError(f"Failed to load checkpoint from {path}: {exc}") from exc

    def list_runs(self) -> list[str]:
        """List all checkpoint run IDs."""
        return sorted(p.stem for p in self.base_dir.glob("*.json"))

    def clear(self, run_id: str) -> None:
        """Delete a checkpoint."""
        path = self._path_for(run_id)
        if path.exists():
            path.unlink()

    def latest(self) -> Checkpoint | None:
        """Return the most recently updated checkpoint, or None."""
        runs = self.list_runs()
        if not runs:
            return None
        checkpoints = [self.load(r) for r in runs]
        checkpoints = [c for c in checkpoints if c is not None]
        if not checkpoints:
            return None
        return max(checkpoints, key=lambda c: c.last_updated)
