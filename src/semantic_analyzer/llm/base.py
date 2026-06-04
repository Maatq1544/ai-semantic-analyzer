"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class UsageStats:
    """Token usage for a single LLM call."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class CompletionRequest:
    """A request to an LLM provider."""

    system_prompt: str
    user_prompt: str
    model: str
    temperature: float = 0.0
    max_tokens: int = 1024
    response_format_json: bool = True
    timeout: int = 60
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    """A response from an LLM provider."""

    content: str
    usage: UsageStats
    model: str
    raw: dict[str, Any] = field(default_factory=dict)

    def parsed_json(self) -> dict[str, Any]:
        """Parse ``content`` as JSON. Returns empty dict on failure."""
        import json

        try:
            return json.loads(self.content)
        except (json.JSONDecodeError, TypeError):
            return {}


class BaseLLMClient(ABC):
    """Abstract LLM client."""

    def __init__(self, api_key: str | None, base_url: str | None, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Run a single completion call.

        Args:
            request: Completion parameters.

        Returns:
            Parsed response with usage stats.

        Raises:
            LLMError: On provider error.
        """
