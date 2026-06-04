# Quickstart

Get from zero to analyzed CSV in 5 minutes.

## 1. Install

```bash
# From the repo root
pip install -e .

# Or with all extras (dev + docs)
pip install -e ".[dev,docs]"
```

Requirements: **Python 3.10+**

## 2. Set your API key

```bash
# DeepSeek (default — best price/performance)
export DEEPSEEK_API_KEY="sk-..."

# Or OpenAI
export OPENAI_API_KEY="sk-..."

# Or Anthropic Claude
export ANTHROPIC_API_KEY="sk-ant-..."

# Or Ollama (local, no key needed)
ollama pull llama3.2
```

## 3. Run analysis

### Quick run

```bash
semantic-analyzer run reviews.csv "Extract sentiment (Positive/Negative/Neutral) and detect sarcasm (true/false)"
```

Output: `analyzed_reviews.csv` in the current directory with the original columns + new ones (e.g., `sentiment`, `sarcasm`).

### Specify provider and output

```bash
semantic-analyzer run reviews.csv "Classify sentiment" \
    --provider anthropic \
    --model claude-3-5-haiku-20241022 \
    --output results.json \
    --output-format json
```

### Use a pre-built task template

```bash
# See available templates
semantic-analyzer tasks

# Use one
semantic-analyzer run tickets.csv "$(semantic-analyzer tasks | grep ticket_classification)"
```

Or just paste the description from the templates list.

### Inspect a file first

```bash
semantic-analyzer info reviews.csv
```

Prints row count, column types, missing values, and a 3-row preview.

### Convert formats

```bash
# CSV → JSON
semantic-analyzer convert data.csv data.json

# JSON → JSONL
semantic-analyzer convert data.json data.jsonl

# CSV → Parquet
semantic-analyzer convert data.csv data.parquet
```

## 4. Generate a config file

```bash
semantic-analyzer init-config
```

Creates `semantic-analyzer.yaml` with all options documented. Edit and pass with `--config`:

```bash
semantic-analyzer --config semantic-analyzer.yaml run input.csv "task"
```

## 5. Chunk large files

For files with 10k+ rows, chunking keeps memory and time predictable:

```bash
# Process 500 rows per chunk
semantic-analyzer run big.csv "task" --chunk-strategy rows --chunk-size 500
```

## 6. Resume after interruption

```bash
# First run (interrupted)
semantic-analyzer run big.csv "task" --chunk-size 500

# Resume
semantic-analyzer run big.csv "task" --chunk-size 500 --resume
```

Checkpoints stored in `.checkpoints/`. List them:

```bash
semantic-analyzer checkpoints
```

## 7. Track cost

Every run prints a summary:

```
╭────────────────── Run Summary ──────────────────╮
│ Rows analyzed   │ 1000                          │
│ Rows failed     │ 2                             │
│ Duration (s)    │ 47.3                          │
│ Total tokens    │ 234,567                       │
│ Total cost      │ $0.0621                       │
│ Output          │ /path/to/analyzed_reviews.csv │
╰──────────────────────────────────────────────────╯
```

## Common flags

| Flag | Description |
|---|---|
| `--provider` | `deepseek` (default), `openai`, `anthropic`, `ollama` |
| `--model` | Provider-specific model name |
| `--output` / `-o` | Output file path |
| `--output-format` / `-f` | `csv`, `json`, `jsonl` |
| `--max-workers` / `-w` | Parallel LLM calls |
| `--chunk-size` | Rows per chunk (with `--chunk-strategy rows`) |
| `--resume` | Resume from checkpoint |
| `--dry-run` | Load + clean but skip LLM calls |
| `--no-clean` | Disable data cleaning |
| `--lowercase` | Lowercase text columns |
| `--verbose` / `-v` | Debug logging |

Run `semantic-analyzer run --help` for the full list.
