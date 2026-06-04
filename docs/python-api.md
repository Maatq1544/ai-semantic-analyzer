# Python API

Use the analyzer programmatically without the CLI.

## Minimal example

```python
from pathlib import Path
from semantic_analyzer import Config, Pipeline

config = Config(provider="deepseek")
pipeline = Pipeline(config)
result = pipeline.run(
    input_path="reviews.csv",
    task_description="Extract sentiment (Positive/Negative/Neutral)",
    output_path="results.csv",
)

print(f"Analyzed {result.rows_analyzed} rows in {result.duration_seconds:.1f}s")
print(f"Cost: ${result.cost_summary['total_cost_usd']}")
```

## Custom cleaning

```python
from semantic_analyzer import Config
from semantic_analyzer.config import CleanConfig

config = Config(
    provider="openai",
    clean=CleanConfig(
        drop_duplicates=True,
        dedupe_subset=["email"],          # dedupe by email column only
        normalize_text=True,
        lowercase_text=True,
        fill_na="UNKNOWN",
    ),
)
```

## Chunked processing

```python
from semantic_analyzer import Config
from semantic_analyzer.config import ChunkStrategy

config = Config(
    chunk_strategy=ChunkStrategy.ROWS,
    chunk_size=500,                        # 500 rows per chunk
)
```

## Custom LLM client

Swap out the LLM client for testing or advanced use:

```python
from semantic_analyzer import Config, Pipeline
from semantic_analyzer.llm.base import BaseLLMClient, CompletionRequest, CompletionResponse, UsageStats

class MyMockClient(BaseLLMClient):
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        return CompletionResponse(
            content='{"sentiment": "Positive"}',
            usage=UsageStats(input_tokens=10, output_tokens=5),
            model=self.model,
        )

config = Config(provider="deepseek")
pipeline = Pipeline(config, client=MyMockClient("k", None, "test"))
result = pipeline.run("data.csv", "Classify sentiment", "out.csv")
```

## Resumable runs

```python
config = Config(resume=True, checkpoint_dir=Path("./.checkpoints"))
pipeline = Pipeline(config)
pipeline.run("huge.csv", "task")  # first run, may fail

# ...later, same run_id, picks up where left off
pipeline.run("huge.csv", "task")
```

## Inspect intermediate state

```python
from semantic_analyzer.data import DataLoader, DataCleaner, Chunker
from semantic_analyzer.config import ChunkStrategy

loader = DataLoader()
df = loader.load("data.csv")
print(f"Loaded {len(df)} rows")

cleaner = DataCleaner()
df_clean, stats = cleaner.clean(df)
print(f"Clean stats: {stats}")

chunker = Chunker(ChunkStrategy.ROWS, chunk_size=100)
for chunk_df, meta in chunker.chunks(df_clean):
    print(f"Chunk {meta.chunk_id}: rows {meta.start_row}-{meta.end_row}, ~{meta.estimated_tokens} tokens")
```

## Cost tracking

```python
from semantic_analyzer.utils.cost import CostCalculator, PRICING_TABLE

# What does it cost to process 1M rows with this model?
print(f"deepseek-chat input: ${PRICING_TABLE['deepseek-chat'].input_per_million}/M tokens")
print(f"gpt-4o output: ${PRICING_TABLE['gpt-4o'].output_per_million}/M tokens")
```

## Custom provider

Register a new provider by subclassing `BaseLLMClient`:

```python
from semantic_analyzer.llm.base import BaseLLMClient, CompletionRequest, CompletionResponse
from semantic_analyzer.llm.registry import LLMRegistry
from semantic_analyzer.config import Provider

class MyProviderClient(BaseLLMClient):
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        # Your implementation
        ...

# Register
LLMRegistry.register(Provider("myprovider"), MyProviderClient)
```

(Note: you'd also need to add `myprovider` to the `Provider` enum.)

## Error handling

```python
from semantic_analyzer import Config, Pipeline
from semantic_analyzer.exceptions import (
    SemanticAnalyzerError,
    ConfigurationError,
    DataError,
    LLMError,
    PipelineError,
)

try:
    pipeline = Pipeline(config)
    result = pipeline.run("data.csv", "task")
except ConfigurationError as exc:
    print(f"Bad config: {exc}")
except DataError as exc:
    print(f"Data problem: {exc}")
except LLMError as exc:
    print(f"LLM failed: {exc}")
except PipelineError as exc:
    print(f"Pipeline failed: {exc}")
```

## Type hints

The full package is fully type-annotated. Run `mypy` against your code:

```bash
mypy --strict your_script.py
```
