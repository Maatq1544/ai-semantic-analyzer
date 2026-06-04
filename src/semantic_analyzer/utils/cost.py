"""Cost calculation and pricing tables."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    """Per-million-token pricing in USD."""

    input_per_million: float
    output_per_million: float


# Pricing as of 2025-2026. Update as providers change.
PRICING_TABLE: dict[str, ModelPricing] = {
    # DeepSeek
    "deepseek-chat": ModelPricing(input_per_million=0.27, output_per_million=1.10),
    "deepseek-reasoner": ModelPricing(input_per_million=0.55, output_per_million=2.19),
    # OpenAI
    "gpt-4o": ModelPricing(input_per_million=2.50, output_per_million=10.00),
    "gpt-4o-mini": ModelPricing(input_per_million=0.15, output_per_million=0.60),
    "gpt-4-turbo": ModelPricing(input_per_million=10.00, output_per_million=30.00),
    "gpt-3.5-turbo": ModelPricing(input_per_million=0.50, output_per_million=1.50),
    # Anthropic
    "claude-3-5-sonnet-20241022": ModelPricing(input_per_million=3.00, output_per_million=15.00),
    "claude-3-5-haiku-20241022": ModelPricing(input_per_million=0.80, output_per_million=4.00),
    "claude-3-opus-20240229": ModelPricing(input_per_million=15.00, output_per_million=75.00),
    # Ollama (local — free)
    "llama3.2": ModelPricing(input_per_million=0.0, output_per_million=0.0),
    "llama3.1": ModelPricing(input_per_million=0.0, output_per_million=0.0),
    "mistral": ModelPricing(input_per_million=0.0, output_per_million=0.0),
    "qwen2.5": ModelPricing(input_per_million=0.0, output_per_million=0.0),
}


class CostCalculator:
    """Accumulates token usage and cost across calls."""

    def __init__(self) -> None:
        self._input_tokens = 0
        self._output_tokens = 0
        self._total_cost = 0.0
        self._call_count = 0
        self._cache_hits = 0

    def record(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> None:
        """Record usage for a single call."""
        self._input_tokens += input_tokens
        self._output_tokens += output_tokens
        self._cache_hits += cached_tokens
        self._call_count += 1

        pricing = PRICING_TABLE.get(model)
        if pricing is None:
            # Unknown model — don't accumulate cost, just tokens
            return

        # Cache hit tokens are charged at a discount (typically 10% of input price)
        billable_input = input_tokens - cached_tokens
        cache_cost = cached_tokens * (pricing.input_per_million * 0.1) / 1_000_000
        input_cost = billable_input * pricing.input_per_million / 1_000_000
        output_cost = output_tokens * pricing.output_per_million / 1_000_000
        self._total_cost += input_cost + output_cost + cache_cost

    @property
    def total_input_tokens(self) -> int:
        return self._input_tokens

    @property
    def total_output_tokens(self) -> int:
        return self._output_tokens

    @property
    def total_tokens(self) -> int:
        return self._input_tokens + self._output_tokens

    @property
    def total_cost(self) -> float:
        return self._total_cost

    @property
    def call_count(self) -> int:
        return self._call_count

    @property
    def cache_hit_rate(self) -> float:
        if self._input_tokens == 0:
            return 0.0
        return self._cache_hits / self._input_tokens

    def summary(self) -> dict[str, float | int]:
        return {
            "calls": self._call_count,
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "total_tokens": self.total_tokens,
            "cached_tokens": self._cache_hits,
            "cache_hit_rate": round(self.cache_hit_rate, 3),
            "total_cost_usd": round(self._total_cost, 4),
        }
