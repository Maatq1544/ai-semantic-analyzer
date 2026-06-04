"""Tests for cost tracking."""

from semantic_analyzer.utils.cost import CostCalculator, PRICING_TABLE


def test_record_known_model() -> None:
    calc = CostCalculator()
    calc.record("gpt-4o-mini", input_tokens=1_000_000, output_tokens=0)
    # 1M input * $0.15/M = $0.15
    assert abs(calc.total_cost - 0.15) < 0.001


def test_record_unknown_model() -> None:
    calc = CostCalculator()
    calc.record("unknown-model", input_tokens=1000, output_tokens=500)
    # Tokens still recorded, cost stays 0
    assert calc.total_input_tokens == 1000
    assert calc.total_output_tokens == 500
    assert calc.total_cost == 0.0


def test_cache_hits() -> None:
    calc = CostCalculator()
    calc.record("deepseek-chat", input_tokens=1000, output_tokens=500, cached_tokens=500)
    summary = calc.summary()
    assert summary["cached_tokens"] == 500
    assert summary["cache_hit_rate"] == 0.5


def test_summary() -> None:
    calc = CostCalculator()
    calc.record("gpt-3.5-turbo", input_tokens=100, output_tokens=50)
    s = calc.summary()
    assert s["calls"] == 1
    assert s["input_tokens"] == 100
    assert s["output_tokens"] == 50
    assert s["total_tokens"] == 150


def test_pricing_table_has_common_models() -> None:
    assert "gpt-4o-mini" in PRICING_TABLE
    assert "claude-3-5-sonnet-20241022" in PRICING_TABLE
    assert "deepseek-chat" in PRICING_TABLE
