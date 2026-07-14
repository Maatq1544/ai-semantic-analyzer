"""Configuration system.

Precedence (high → low):
  1. CLI arguments (passed to ``Config.from_cli_overrides``)
  2. YAML file (``--config`` flag, default ``semantic-analyzer.yaml``)
  3. Environment variables (with ``SEMANTIC_`` prefix and provider-specific prefixes)
  4. ``.env`` file (loaded via ``python-dotenv``)
  5. Built-in defaults
"""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env once at module import — idempotent.
load_dotenv()


class Provider(str, Enum):
    """Supported LLM providers."""

    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"


class OutputFormat(str, Enum):
    """Output file formats."""

    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"


class ChunkStrategy(str, Enum):
    """How to chunk large datasets."""

    NONE = "none"  # No chunking; process all rows as one batch
    ROWS = "rows"  # Fixed number of rows per chunk
    TOKENS = "tokens"  # Approximate token-based chunking


class CleanConfig(BaseModel):
    """Data cleaning configuration."""

    drop_duplicates: bool = True
    """Remove exact duplicate rows."""

    dedupe_subset: list[str] | None = None
    """If set, only consider these columns when deduplicating."""

    drop_empty_rows: bool = True
    """Remove rows where all values are NaN/empty."""

    drop_empty_subset: list[str] | None = None
    """If set, drop rows where ALL of these columns are empty."""

    normalize_text: bool = True
    """Apply text normalization (whitespace, unicode) to string columns."""

    lowercase_text: bool = False
    """Lowercase all text columns (off by default)."""

    trim_whitespace: bool = True
    """Strip leading/trailing whitespace from string columns."""

    fill_na: str | None = None
    """If set, fill NaN values with this string. None = keep as NaN."""


class ProviderConfig(BaseModel):
    """Provider-specific configuration."""

    api_key: str | None = None
    base_url: str | None = None
    model: str = "deepseek-chat"

    @field_validator("api_key")
    @classmethod
    def _no_empty_key(cls, v: str | None) -> str | None:
        if v is not None and v.strip() == "":
            return None
        return v


class Config(BaseSettings):
    """Main configuration container.

    Built via :meth:`load` from a layered source. CLI overrides are applied via
    :meth:`with_overrides` which returns a new instance.
    """

    model_config = SettingsConfigDict(
        env_prefix="SEMANTIC_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Pipeline
    provider: Provider = Provider.DEEPSEEK
    output_format: OutputFormat = OutputFormat.CSV
    batch_size: int = Field(default=10, ge=1, le=1000)
    max_workers: int = Field(default=5, ge=1, le=100)
    chunk_size: int = Field(default=0, ge=0, le=100_000)
    chunk_strategy: ChunkStrategy = ChunkStrategy.NONE
    timeout: int = Field(default=60, ge=5, le=600)
    max_retries: int = Field(default=3, ge=0, le=10)
    log_level: str = "INFO"

    # Cleaning
    clean: CleanConfig = Field(default_factory=CleanConfig)

    # Provider configs (one per provider, lazy-loaded)
    deepseek: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            base_url="https://api.deepseek.com",
            model="deepseek-chat",
        )
    )
    openai: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            base_url="https://api.openai.com/v1",
            model="gpt-4o-mini",
        )
    )
    anthropic: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            model="claude-3-5-sonnet-20241022",
        )
    )
    ollama: ProviderConfig = Field(
        default_factory=lambda: ProviderConfig(
            base_url="http://localhost:11434",
            model="llama3.2",
        )
    )

    # Pipeline options
    resume: bool = False
    """Resume from the most recent checkpoint if one exists."""

    checkpoint_dir: Path = Path(".checkpoints")
    """Where to store checkpoint files."""

    dry_run: bool = False
    """If True, load + clean + chunk but do not call the LLM."""

    show_progress: bool = True
    """Display a Rich progress bar during processing."""

    # Custom system prompt
    system_prompt: str | None = None
    """Inline system prompt. Overrides the default template when set."""

    system_prompt_file: Path | None = None
    """Path to a file containing the system prompt. Takes precedence over
    ``system_prompt`` if both are set."""

    @model_validator(mode="after")
    def _validate_chunk_strategy(self) -> Config:
        if self.chunk_strategy == ChunkStrategy.ROWS and self.chunk_size == 0:
            raise ValueError("chunk_size must be > 0 when chunk_strategy='rows'")
        if self.chunk_strategy == ChunkStrategy.TOKENS and self.chunk_size == 0:
            raise ValueError("chunk_size must be > 0 when chunk_strategy='tokens'")
        return self

    @property
    def active_provider_config(self) -> ProviderConfig:
        """Return the configuration for the currently active provider."""
        return getattr(self, self.provider.value)

    @property
    def effective_api_key(self) -> str | None:
        """Return the API key for the active provider, or None if not required."""
        cfg = self.active_provider_config
        if cfg.api_key:
            return cfg.api_key
        # Ollama doesn't require an API key
        if self.provider == Provider.OLLAMA:
            return "ollama"
        return None

    @property
    def effective_base_url(self) -> str | None:
        """Return the base URL for the active provider."""
        return self.active_provider_config.base_url

    @property
    def effective_model(self) -> str:
        """Return the model name for the active provider."""
        return self.active_provider_config.model

    @property
    def effective_system_prompt(self) -> str | None:
        """Return the custom system prompt, loading from file if specified.

        Supports ``.txt``, ``.md`` (text) and ``.docx`` (extracted via
        ``python-docx``).  Returns ``None`` when no custom prompt is
        configured, meaning the pipeline should use the built-in template.
        """
        if self.system_prompt_file is not None:
            path = Path(self.system_prompt_file)
            if not path.exists():
                return self.system_prompt
            if path.suffix.lower() == ".docx":
                return self._read_docx(path)
            return path.read_text(encoding="utf-8")
        return self.system_prompt

    @staticmethod
    def _read_docx(path: Path) -> str:
        """Extract text from a .docx file."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx is required to read .docx prompts. "
                "Install it with: pip install python-docx"
            )
        doc = Document(str(path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    @classmethod
    def from_env(cls) -> Config:
        """Build config from environment variables and .env file only."""
        # Pull provider-specific env vars
        env_overrides: dict[str, Any] = {}

        for provider_name in ("deepseek", "openai", "anthropic", "ollama"):
            prefix = provider_name.upper()
            api_key = os.getenv(f"{prefix}_API_KEY")
            base_url = os.getenv(f"{prefix}_BASE_URL")
            model = os.getenv(f"{prefix}_MODEL")
            provider_cfg: dict[str, Any] = {}
            if api_key:
                provider_cfg["api_key"] = api_key
            if base_url:
                provider_cfg["base_url"] = base_url
            if model:
                provider_cfg["model"] = model
            if provider_cfg:
                env_overrides[provider_name] = provider_cfg

        return cls(**env_overrides)

    @classmethod
    def load(cls, config_path: Path | str | None = None) -> Config:
        """Build config from layered sources.

        Precedence: YAML file (if given) → env vars → .env → defaults.
        """
        env_config = cls.from_env()

        if config_path is None:
            for candidate in ("semantic-analyzer.yaml", "semantic-analyzer.yml"):
                if Path(candidate).exists():
                    config_path = candidate
                    break

        if config_path is None or not Path(config_path).exists():
            return env_config

        # YAML provides additional defaults; env still wins
        with open(config_path) as f:
            yaml_data = yaml.safe_load(f) or {}

        return cls(**{**yaml_data, **env_config.model_dump(exclude_unset=True)})

    def with_overrides(self, **overrides: Any) -> Config:
        """Return a new Config with the given fields overridden."""
        merged = self.model_dump()
        for key, value in overrides.items():
            if value is None:
                continue
            if key in {"deepseek", "openai", "anthropic", "ollama"} and isinstance(value, dict):
                merged.setdefault(key, {}).update(value)
            else:
                merged[key] = value
        return Config(**merged)
