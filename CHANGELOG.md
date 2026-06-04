# Changelog

All notable changes to AI Semantic Analyzer are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] — 2026-06-05

### Added

- Initial stable release
- Full pipeline: load → clean → chunk → analyze → write
- CLI with subcommands: `run`, `convert`, `info`, `tasks`, `init-config`, `checkpoints`
- Multi-provider support: DeepSeek, OpenAI, Anthropic, Ollama
- OpenAI-compatible endpoint support (LM Studio, vLLM, Together, Groq)
- Pydantic-based configuration with layered loading (CLI > YAML > env > .env > defaults)
- Data cleaning: dedupe, normalize text, trim whitespace, fill NaN, lowercase
- Chunking strategies: none, by-rows, by-tokens
- Resumable checkpoint system
- Cost tracking with per-model pricing table
- Rate limiting and exponential-backoff retry
- Output formats: CSV, JSON, JSONL
- Pre-built task templates: sentiment, lead scoring, ticket classification, review analysis
- Structured logging via structlog
- Rich progress bars and colored output
- Python API for programmatic use
- AI Agent skill (`skills/dataset-processor/`) for end-to-end dataset processing
- Comprehensive test suite (60+ tests)
- Documentation: quickstart, configuration, Python API
- GitHub workflows: CI, release-please, link-check, stale, codeql
- PR and issue templates, FUNDING, CODEOWNERS, dependabot config

### Changed

- Migrated from single-file script to proper Python package with `src/` layout
- Configuration system rewritten with Pydantic v2
- LLM client architecture now uses provider registry pattern

### Removed

- Personal data from repository metadata and documentation
- Hardcoded configuration that bypassed environment variables
- Direct script execution in favor of proper CLI entry point
