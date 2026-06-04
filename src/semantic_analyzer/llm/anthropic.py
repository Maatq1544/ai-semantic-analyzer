"""Anthropic Claude client."""

from __future__ import annotations

import time
from typing import Any

from anthropic import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError,
)

from semantic_analyzer.exceptions import (
    LLMError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from semantic_analyzer.llm.base import (
    BaseLLMClient,
    CompletionRequest,
    CompletionResponse,
    UsageStats,
)
from semantic_analyzer.utils.cost import PRICING_TABLE
from semantic_analyzer.utils.logging import get_logger
from semantic_analyzer.utils.retry import retry

logger = get_logger(__name__)


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models."""

    def __init__(
        self,
        api_key: str | None,
        base_url: str | None,
        model: str,
        max_retries: int = 3,
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, model=model)
        self.max_retries = max_retries
        # Import here so the dep is only needed when used
        from anthropic import Anthropic

        kwargs: dict[str, Any] = {"api_key": api_key or ""}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = Anthropic(**kwargs)

    @retry(max_attempts=3, base_delay=1.0, max_delay=30.0)
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Run a Claude completion with retry-on-rate-limit / timeout."""
        start = time.time()
        try:
            kwargs: dict[str, Any] = {
                "model": request.model or self.model,
                "system": request.system_prompt,
                "messages": [{"role": "user", "content": request.user_prompt}],
                "temperature": request.temperature,
                "max_tokens": request.max_tokens or 1024,
                "timeout": request.timeout,
            }
            response = self._client.messages.create(**kwargs)
        except RateLimitError as exc:
            logger.warning("anthropic_rate_limit", error=str(exc))
            raise LLMRateLimitError(str(exc)) from exc
        except APITimeoutError as exc:
            logger.warning("anthropic_timeout", timeout=request.timeout)
            raise LLMTimeoutError(str(exc)) from exc
        except APIConnectionError as exc:
            logger.warning("anthropic_connection_error", error=str(exc))
            raise LLMError(f"Connection error: {exc}") from exc
        except AuthenticationError as exc:
            raise LLMError(f"Authentication failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Unexpected Anthropic error: {exc}") from exc

        # Extract usage
        usage = UsageStats(
            input_tokens=getattr(response.usage, "input_tokens", 0) or 0,
            output_tokens=getattr(response.usage, "output_tokens", 0) or 0,
            cached_tokens=getattr(response.usage, "cache_read_input_tokens", 0) or 0,
        )

        # Extract content
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        duration = time.time() - start
        logger.debug(
            "anthropic_call_complete",
            model=request.model or self.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            duration_s=round(duration, 2),
        )

        return CompletionResponse(
            content=content,
            usage=usage,
            model=request.model or self.model,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )

    @property
    def supports_json_mode(self) -> bool:
        """Claude doesn't have a native JSON mode — we instruct it in the prompt."""
        return False

    @property
    def has_pricing(self) -> bool:
        return self.model in PRICING_TABLE
