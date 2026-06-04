"""OpenAI-compatible LLM client (DeepSeek, OpenAI, Ollama, etc.)."""

from __future__ import annotations

import time
from typing import Any

from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
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


class OpenAICompatibleClient(BaseLLMClient):
    """Client for any OpenAI-API-compatible service.

    Works with: DeepSeek, OpenAI, Ollama, LM Studio, vLLM, Together, Groq, etc.
    Just point ``base_url`` at the right endpoint.
    """

    def __init__(
        self,
        api_key: str | None,
        base_url: str | None,
        model: str,
        max_retries: int = 3,
    ) -> None:
        super().__init__(api_key=api_key, base_url=base_url, model=model)
        self.max_retries = max_retries
        self._client = OpenAI(api_key=api_key or "sk-no-key", base_url=base_url, max_retries=0)

    @retry(max_attempts=3, base_delay=1.0, max_delay=30.0)
    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Run a completion with retry-on-rate-limit / timeout."""
        start = time.time()
        try:
            kwargs: dict[str, Any] = {
                "model": request.model or self.model,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": request.user_prompt},
                ],
                "temperature": request.temperature,
                "timeout": request.timeout,
            }
            if request.max_tokens:
                kwargs["max_tokens"] = request.max_tokens
            if request.response_format_json:
                kwargs["response_format"] = {"type": "json_object"}

            response = self._client.chat.completions.create(**kwargs)
        except RateLimitError as exc:
            logger.warning("rate_limit_hit", error=str(exc))
            raise LLMRateLimitError(str(exc)) from exc
        except APITimeoutError as exc:
            logger.warning("api_timeout", timeout=request.timeout)
            raise LLMTimeoutError(str(exc)) from exc
        except APIConnectionError as exc:
            logger.warning("api_connection_error", error=str(exc))
            raise LLMError(f"Connection error: {exc}") from exc
        except AuthenticationError as exc:
            raise LLMError(f"Authentication failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Unexpected LLM error: {exc}") from exc

        # Extract usage
        usage = UsageStats()
        if hasattr(response, "usage") and response.usage:
            usage.input_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
            usage.output_tokens = getattr(response.usage, "completion_tokens", 0) or 0
            cached = getattr(response.usage, "cached_tokens", 0) or 0
            # Some providers report cached tokens under prompt_tokens_details
            if not cached and hasattr(response.usage, "prompt_tokens_details"):
                details = response.usage.prompt_tokens_details
                cached = getattr(details, "cached_tokens", 0) or 0
            usage.cached_tokens = cached

        # Extract content
        content = ""
        if response.choices:
            content = response.choices[0].message.content or ""

        duration = time.time() - start
        logger.debug(
            "llm_call_complete",
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
        """Most OpenAI-compatible providers support ``response_format=json_object``."""
        return True

    @property
    def has_pricing(self) -> bool:
        return self.model in PRICING_TABLE
