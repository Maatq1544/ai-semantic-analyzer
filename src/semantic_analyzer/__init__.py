"""AI Semantic Analyzer — Industrial-grade LLM pipeline for CSV/Excel text analysis.

This package provides a complete pipeline for processing tabular data with
Large Language Models:

- **Load** CSV, Excel, JSON, JSONL, Parquet files
- **Clean** data with configurable rules (deduplication, normalization, etc.)
- **Chunk** large datasets into manageable pieces
- **Analyze** with LLM providers (DeepSeek, OpenAI, Anthropic, Ollama)
- **Export** to CSV, JSON, JSONL with cost tracking

Quickstart:

    >>> from semantic_analyzer import Pipeline, Config
    >>> config = Config(provider="deepseek", model="deepseek-chat")
    >>> pipeline = Pipeline(config)
    >>> pipeline.run("data.csv", "Analyze sentiment", "results.csv")
"""

from semantic_analyzer.config import Config
from semantic_analyzer.exceptions import (
    SemanticAnalyzerError,
    ConfigurationError,
    DataError,
    LLMError,
    PipelineError,
)
from semantic_analyzer.pipeline import Pipeline

__version__ = "1.0.0"
__author__ = "AI Semantic Analyzer Contributors"
__license__ = "MIT"

__all__ = [
    "Config",
    "Pipeline",
    "SemanticAnalyzerError",
    "ConfigurationError",
    "DataError",
    "LLMError",
    "PipelineError",
    "__version__",
]
