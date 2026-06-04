"""Tests for the config system."""

import os
from pathlib import Path

import pytest

from semantic_analyzer.config import (
    ChunkStrategy,
    CleanConfig,
    Config,
    OutputFormat,
    Provider,
)
from semantic_analyzer.exceptions import ConfigurationError


def test_default_config() -> None:
    config = Config()
    assert config.provider == Provider.DEEPSEEK
    assert config.output_format == OutputFormat.CSV
    assert config.batch_size == 10


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
    config = Config.from_env()
    assert config.deepseek.api_key == "sk-test"


def test_invalid_chunk_strategy() -> None:
    with pytest.raises(ValueError):
        Config(chunk_strategy=ChunkStrategy.ROWS, chunk_size=0)


def test_config_overrides() -> None:
    base = Config()
    override = base.with_overrides(provider="openai", max_workers=20)
    assert override.provider == Provider.OPENAI
    assert override.max_workers == 20
    # Original unchanged
    assert base.provider == Provider.DEEPSEEK


def test_config_load_yaml(tmp_path: Path) -> None:
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text("provider: openai\nmax_workers: 15\n")
    config = Config.load(yaml_path)
    assert config.provider == Provider.OPENAI
    assert config.max_workers == 15


def test_active_provider_config() -> None:
    config = Config(provider=Provider.ANTHROPIC)
    assert config.active_provider_config.model == "claude-3-5-sonnet-20241022"


def test_effective_model() -> None:
    config = Config()
    assert config.effective_model == "deepseek-chat"
