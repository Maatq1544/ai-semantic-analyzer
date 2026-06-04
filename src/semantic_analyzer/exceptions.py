"""Custom exceptions for the semantic_analyzer package."""


class SemanticAnalyzerError(Exception):
    """Base exception for all semantic_analyzer errors."""


class ConfigurationError(SemanticAnalyzerError):
    """Raised when configuration is invalid or missing required values."""


class DataError(SemanticAnalyzerError):
    """Raised when data loading, cleaning, or writing fails."""


class ChunkingError(SemanticAnalyzerError):
    """Raised when chunking produces invalid results."""


class LLMError(SemanticAnalyzerError):
    """Raised when an LLM provider call fails."""


class LLMRateLimitError(LLMError):
    """Raised when the LLM provider returns a rate limit response."""


class LLMTimeoutError(LLMError):
    """Raised when the LLM provider times out."""


class PipelineError(SemanticAnalyzerError):
    """Raised when pipeline execution fails irrecoverably."""


class CheckpointError(SemanticAnalyzerError):
    """Raised when checkpoint save/load fails."""
