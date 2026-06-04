# Contributing to AI Semantic Analyzer

Thank you for your interest in contributing! This document covers the basics of getting started.

## Code of Conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/). By participating, you agree to uphold its principles. Be respectful, be constructive, focus on the work.

## How to contribute

### Reporting bugs

Open an issue with the **bug report** template. Include:

- Minimal reproduction steps
- Expected vs actual behavior
- Python version, OS, `semantic-analyzer --version`
- Relevant logs (run with `-v` for debug output)

### Suggesting features

Open an issue with the **feature request** template. Explain:

- The problem you're trying to solve
- Your proposed solution
- Alternatives you've considered
- Use cases

### Submitting code

1. **Fork** the repo
2. **Branch** from `main`: `git checkout -b feat/your-feature`
3. **Install** dev deps: `pip install -e ".[dev]"`
4. **Code** with tests
5. **Verify** locally:
   ```bash
   pytest                    # run all tests
   ruff check .              # lint
   ruff format .             # format
   mypy src/semantic_analyzer # type check
   ```
6. **Commit** with [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` docs only
   - `refactor:` code change without behavior change
   - `test:` adding tests
   - `chore:` tooling, deps, etc.
7. **Push** and open a **Pull Request** with the PR template filled out

## Development setup

```bash
git clone https://github.com/Maatq1544/ai-semantic-analyzer.git
cd ai-semantic-analyzer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Try the CLI
semantic-analyzer --help
semantic-analyzer info examples/sample_reviews.csv
```

## Project structure

```
src/semantic_analyzer/    # Main package
├── cli.py                # Click CLI entry point
├── config.py             # Pydantic configuration
├── data/                 # Loaders, writers, cleaners, chunkers
├── llm/                  # Provider clients (OpenAI-compat, Anthropic)
├── pipeline/             # Orchestrator, checkpoint, progress
├── prompts/              # Prompt templates
├── utils/                # Cost, logging, retry
└── exceptions.py

tests/                    # pytest test suite
docs/                     # User documentation
examples/                 # Sample data + config
skills/                   # AI agent skills
.github/                  # GitHub workflows + templates
```

## Adding a new LLM provider

1. Subclass `BaseLLMClient` in `src/semantic_analyzer/llm/`
2. Add the provider to the `Provider` enum in `config.py`
3. Register the client in `llm/registry.py`
4. Add pricing to `utils/cost.py` PRICING_TABLE
5. Add tests
6. Update docs

## Adding a new task template

Edit `src/semantic_analyzer/prompts/templates.py` and add to `DEFAULT_TASKS`. Include it in tests.

## Adding a new output format

1. Add the format to the `OutputFormat` enum in `data/writer.py`
2. Implement the write logic
3. Add tests
4. Update CLI choices in `cli.py`

## Release process

Releases are automated via [release-please](https://github.com/googleapis/release-please):

1. Merge PRs with `feat:`, `fix:`, `perf:` commits
2. release-please opens a Release PR with version bump + CHANGELOG update
3. Merging the Release PR creates a GitHub release and tags the version

## Questions?

Open a [Discussion](https://github.com/Maatq1544/ai-semantic-analyzer/discussions) — not an issue.
