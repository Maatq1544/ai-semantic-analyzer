# Configuration

AI Semantic Analyzer reads configuration from multiple sources. Higher-priority sources override lower-priority ones.

## Precedence (high → low)

1. **CLI flags** — explicit per-invocation overrides
2. **YAML config** — via `--config path.yaml` or auto-detected `semantic-analyzer.yaml`
3. **Environment variables** — `SEMANTIC_*` for general, `PROVIDER_*` for provider-specific
4. **`.env` file** — auto-loaded by `python-dotenv` at startup
5. **Built-in defaults**

## YAML config

Generate a starter:

```bash
semantic-analyzer init-config
```

Full reference (see `examples/semantic-analyzer.yaml`):

```yaml
provider: deepseek
output_format: csv
batch_size: 10
max_workers: 5
chunk_size: 0
chunk_strategy: none     # none | rows | tokens
timeout: 60
max_retries: 3
log_level: INFO

deepseek:
  api_key: ${DEEPSEEK_API_KEY}
  base_url: https://api.deepseek.com
  model: deepseek-chat

openai:
  api_key: ${OPENAI_API_KEY}
  base_url: https://api.openai.com/v1
  model: gpt-4o-mini

anthropic:
  api_key: ${ANTHROPIC_API_KEY}
  model: claude-3-5-sonnet-20241022

ollama:
  base_url: http://localhost:11434
  model: llama3.2

clean:
  drop_duplicates: true
  drop_empty_rows: true
  normalize_text: true
  trim_whitespace: true
  lowercase_text: false
  fill_na: null
  dedupe_subset: null   # e.g. ["email"]
```

## Environment variables

All `SEMANTIC_*` env vars are read automatically (case-insensitive):

| Variable | Default | Description |
|---|---|---|
| `SEMANTIC_PROVIDER` | `deepseek` | `deepseek`, `openai`, `anthropic`, `ollama` |
| `SEMANTIC_OUTPUT_FORMAT` | `csv` | `csv`, `json`, `jsonl` |
| `SEMANTIC_BATCH_SIZE` | `10` | Rows per parallel batch |
| `SEMANTIC_MAX_WORKERS` | `5` | Concurrent LLM calls |
| `SEMANTIC_CHUNK_SIZE` | `0` | Chunk size (0 = no chunking) |
| `SEMANTIC_CHUNK_STRATEGY` | `none` | `none`, `rows`, `tokens` |
| `SEMANTIC_TIMEOUT` | `60` | Per-request timeout (seconds) |
| `SEMANTIC_MAX_RETRIES` | `3` | Retries on transient errors |
| `SEMANTIC_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Provider-specific:

| Variable | Description |
|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `DEEPSEEK_BASE_URL` | Override DeepSeek endpoint (default: `https://api.deepseek.com`) |
| `DEEPSEEK_MODEL` | Model name (default: `deepseek-chat`) |
| `OPENAI_API_KEY` | OpenAI API key |
| `OPENAI_BASE_URL` | OpenAI-compatible endpoint (for LM Studio, vLLM, etc.) |
| `OPENAI_MODEL` | OpenAI model name |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `ANTHROPIC_MODEL` | Claude model name |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434`) |
| `OLLAMA_MODEL` | Ollama model name |

## Using a custom OpenAI-compatible endpoint

The OpenAI client works with any service that exposes an OpenAI-compatible API. Point `base_url` at it:

```bash
# LM Studio
export OPENAI_BASE_URL="http://localhost:1234/v1"
export OPENAI_API_KEY="lm-studio"

# vLLM
export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="dummy"

# Together AI
export OPENAI_BASE_URL="https://api.together.xyz/v1"
export OPENAI_API_KEY="..."

# Groq
export OPENAI_BASE_URL="https://api.groq.com/openai/v1"
export OPENAI_API_KEY="gsk_..."
```

Then `semantic-analyzer run ... --provider openai` works against any of them.

## Chaining configs

You can layer configs: defaults → `.env` → YAML → CLI flags. The CLI always wins for explicitly-passed flags.

Example workflow:

1. `.env` has `DEEPSEEK_API_KEY` and `OPENAI_BASE_URL=https://api.openai.com/v1`
2. `prod-config.yaml` has `provider: openai`, `model: gpt-4o`
3. CLI: `semantic-analyzer --config prod-config.yaml run ... --max-workers 20`

Result: provider/model from YAML, workers overridden to 20, API keys from `.env`.

## Validating config

```python
from semantic_analyzer import Config
config = Config.load("my-config.yaml")
print(config.model_dump_json(indent=2))
```

Pydantic validates types and required fields on load. Misconfigurations fail fast with clear error messages.
