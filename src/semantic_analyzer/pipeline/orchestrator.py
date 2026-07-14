"""Main pipeline orchestrator: load → clean → chunk → analyze → write."""

from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_analyzer.config import Config, OutputFormat
from semantic_analyzer.data import (
    Chunker,
    ChunkStrategy,
    CleanConfig,
    DataCleaner,
    DataLoader,
    DataWriter,
)
from semantic_analyzer.data.chunker import ChunkMetadata
from semantic_analyzer.exceptions import PipelineError
from semantic_analyzer.llm.base import BaseLLMClient, CompletionRequest
from semantic_analyzer.llm.registry import get_client
from semantic_analyzer.pipeline.checkpoint import Checkpoint, CheckpointStore
from semantic_analyzer.pipeline.progress import (
    print,
    print_error,
    print_header,
    print_success,
    print_summary,
    print_warning,
    progress_bar,
)
from semantic_analyzer.prompts.templates import build_system_prompt, build_user_prompt
from semantic_analyzer.utils.cost import CostCalculator
from semantic_analyzer.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineResult:
    """Outcome of a single pipeline run."""

    output_path: Path
    rows_analyzed: int
    rows_failed: int
    duration_seconds: float
    cost_summary: dict[str, float | int]
    checkpoint_path: Path | None = None
    stats: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    """End-to-end analysis pipeline.

    Lifecycle:
      1. ``load()`` — read input file into a DataFrame
      2. ``clean()`` — dedupe, normalize, drop empties
      3. ``chunk()`` — split into manageable pieces
      4. ``analyze()`` — run the LLM over each row in parallel
      5. ``merge()`` — combine original + LLM results
      6. ``write()`` — emit output file
    """

    def __init__(
        self,
        config: Config,
        client: BaseLLMClient | None = None,
    ) -> None:
        self.config = config
        self.client = client or get_client(config)
        self.loader = DataLoader()
        self.cleaner = DataCleaner(config.clean)
        self.writer = DataWriter()
        self.cost = CostCalculator()
        self.checkpoint_store = CheckpointStore(config.checkpoint_dir)

    def run(
        self,
        input_path: Path | str,
        task_description: str,
        output_path: Path | str | None = None,
    ) -> PipelineResult:
        """Run the full pipeline end-to-end.

        Args:
            input_path: CSV/Excel/JSON/JSONL file to analyze.
            task_description: Natural-language description of what the LLM
                should extract (e.g. "Extract sentiment, sarcasm, and topic").
            output_path: Where to write results. Defaults to
                ``analyzed_{basename}`` in the current directory.

        Returns:
            :class:`PipelineResult` with stats and output path.

        Raises:
            PipelineError: On irrecoverable failure.
        """
        start = time.time()
        input_path = Path(input_path)
        output_path = self._resolve_output_path(input_path, output_path)
        run_id = self._make_run_id(input_path, task_description)

        print_header(f"Pipeline run {run_id[:8]}")
        print(f"  input:   {input_path}")
        print(f"  output:  {output_path}")
        print(f"  provider: {self.config.provider.value} / {self.config.effective_model}")
        print(f"  workers: {self.config.max_workers}")
        print(f"  chunk:   {self.config.chunk_strategy.value} / size={self.config.chunk_size}")

        # Resume handling
        checkpoint: Checkpoint | None = None
        if self.config.resume:
            checkpoint = self.checkpoint_store.load(run_id)
            if checkpoint:
                print_warning(f"Resuming from checkpoint: {len(checkpoint.completed_chunk_ids)} chunks done")
            else:
                print("No checkpoint found — starting fresh")

        # 1. Load
        df = self.loader.load(input_path)
        print_success(f"Loaded {len(df)} rows × {len(df.columns)} columns from {input_path.name}")

        # 2. Clean
        df_clean, clean_stats = self.cleaner.clean(df)
        print_success(
            f"Cleaned: {clean_stats.get('input_rows', 0)} → {clean_stats.get('output_rows', 0)} rows"
        )
        for key, value in clean_stats.items():
            if key.startswith("dropped_") and value:
                logger.info("cleaning.stat", stat=key, count=value)

        if self.config.dry_run:
            return PipelineResult(
                output_path=output_path,
                rows_analyzed=0,
                rows_failed=0,
                duration_seconds=time.time() - start,
                cost_summary=self.cost.summary(),
                stats={**clean_stats, "dry_run": True},
            )

        # Initialize checkpoint
        if checkpoint is None:
            checkpoint = Checkpoint(
                run_id=run_id,
                input_path=str(input_path),
                task_description=task_description,
                started_at=time.time(),
                last_updated=time.time(),
                total_rows=len(df_clean),
                config_snapshot=self.config.model_dump(mode="json"),
            )

        # 3. Chunk
        chunker = Chunker(self.config.chunk_strategy, self.config.chunk_size)
        all_chunks = list(chunker.chunks(df_clean))
        checkpoint.total_chunks = len(all_chunks)
        print_success(f"Split into {len(all_chunks)} chunks")

        # 4. Analyze
        all_results: list[dict[str, Any]] = []
        rows_failed = 0

        with progress_bar(self.config.show_progress) as progress:
            task_id = (
                progress.add_task("Analyzing rows", total=len(df_clean)) if progress else None
            )

            for chunk_df, meta in all_chunks:
                if checkpoint.is_chunk_done(meta.chunk_id):
                    # Reuse cached results
                    for i in range(meta.row_count):
                        key = f"{meta.chunk_id}:{i}"
                        if key in checkpoint.chunk_results:
                            all_results.append(checkpoint.chunk_results[key])
                    if progress and task_id is not None:
                        progress.update(task_id, advance=meta.row_count)
                    continue

                chunk_results = self._process_chunk(chunk_df, meta, task_description)
                checkpoint.mark_chunk_done(meta.chunk_id, chunk_results)
                self.checkpoint_store.save(checkpoint)

                rows_failed += sum(1 for r in chunk_results if "analysis_error" in r)
                all_results.extend(chunk_results)

                if progress and task_id is not None:
                    progress.update(task_id, advance=meta.row_count)

        # 5. Merge
        result_df = pd.DataFrame(all_results) if all_results else pd.DataFrame()
        # Align indices: chunk results were captured in order, original df was reordered by clean
        merged = pd.concat(
            [df_clean.reset_index(drop=True), result_df.reset_index(drop=True)],
            axis=1,
        )

        # 6. Write
        output_format = self.config.output_format
        written = self.writer.write(merged, output_path, fmt=output_format)
        print_success(f"Wrote {len(merged)} rows to {written}")

        duration = time.time() - start
        cost = self.cost.summary()
        checkpoint.last_updated = time.time()
        ckpt_path = self.checkpoint_store.save(checkpoint)

        result = PipelineResult(
            output_path=written,
            rows_analyzed=len(merged) - rows_failed,
            rows_failed=rows_failed,
            duration_seconds=duration,
            cost_summary=cost,
            checkpoint_path=ckpt_path,
            stats=clean_stats,
        )
        print_summary(
            {
                "Rows analyzed": result.rows_analyzed,
                "Rows failed": result.rows_failed,
                "Duration (s)": round(result.duration_seconds, 2),
                "Total tokens": cost["total_tokens"],
                "Total cost (USD)": f"${cost['total_cost_usd']}",
                "Output": str(written),
            }
        )
        return result

    def _process_chunk(
        self,
        chunk: pd.DataFrame,
        meta: ChunkMetadata,
        task_description: str,
    ) -> list[dict[str, Any]]:
        """Process a single chunk by calling the LLM in parallel for each row."""
        columns = chunk.columns.tolist()
        rows = chunk.to_dict(orient="records")

        results: list[dict[str, Any] | None] = [None] * len(rows)

        def process_one(idx: int, row: dict[str, str]) -> None:
            try:
                user_prompt = build_user_prompt(row, columns, task_description)
                system_prompt = self.config.effective_system_prompt or build_system_prompt(self.config.provider.value)
                request = CompletionRequest(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    model=self.config.effective_model,
                    temperature=0.0,
                    max_tokens=1024,
                    response_format_json=True,
                    timeout=self.config.timeout,
                )
                response = self.client.complete(request)
                self.cost.record(
                    model=response.model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    cached_tokens=response.usage.cached_tokens,
                )
                results[idx] = response.parsed_json()
            except Exception as exc:  # noqa: BLE001
                logger.error("row_failed", error=str(exc), chunk_id=meta.chunk_id, row=idx)
                results[idx] = {"analysis_error": str(exc)}

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = [executor.submit(process_one, i, r) for i, r in enumerate(rows)]
            for f in as_completed(futures):
                exc = f.exception()
                if exc is not None:
                    logger.error("future_failed", error=str(exc))

        # Fill any None slots with error dict
        return [r if r is not None else {"analysis_error": "unknown"} for r in results]

    def _resolve_output_path(
        self, input_path: Path, output_path: Path | str | None
    ) -> Path:
        if output_path is None:
            suffix = self.config.output_format.extension
            return Path(f"analyzed_{input_path.stem}.{suffix}")
        return Path(output_path)

    @staticmethod
    def _make_run_id(input_path: Path, task_description: str) -> str:
        content = f"{input_path.absolute()}:{task_description}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


def run_from_cli(
    input_path: str,
    task: str,
    output: str | None = None,
    **overrides: Any,
) -> PipelineResult:
    """Convenience function for CLI use.

    Loads config from env, applies CLI overrides, runs the pipeline.
    """
    from semantic_analyzer.utils.logging import setup_logging

    config = Config.load().with_overrides(**overrides)
    setup_logging(config)
    pipeline = Pipeline(config)
    return pipeline.run(input_path, task, output)
