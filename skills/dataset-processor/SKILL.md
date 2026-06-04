---
name: dataset-processor
description: >
  End-to-end workflow for processing a raw user dataset with the AI Semantic
  Analyzer. Use this skill when a user provides a CSV/Excel/JSON/JSONL file
  and wants to extract structured insights, classify text, score sentiment,
  detect entities, or do any LLM-powered tabular analysis. The skill walks
  the agent through inspection → cleaning → task design → execution →
  interpretation → reporting. Built around the `semantic-analyzer` CLI.
version: 1.0.0
author: AI Semantic Analyzer Contributors
tags: [dataset, csv, excel, llm, semantic-analysis, pipeline, data-cleaning, nlp]
---

# Dataset Processor

End-to-end workflow for taking a raw user dataset and producing structured
LLM-analyzed output. Designed to be driven by an AI agent (Claude or
equivalent) that has access to a shell.

## When to invoke

Invoke this skill when:

- The user uploads/shares a CSV, Excel, JSON, JSONL, or Parquet file
- The user wants to extract sentiment, classify text, score leads, detect
  sarcasm, extract entities, summarize text, or any other LLM analysis
  applied row-by-row
- The user asks "analyze this dataset" / "process my data" / "classify my
  reviews" / "score my leads" / similar
- The user has a `data.csv` and wants to know what's in it before deciding
  what to extract

Do NOT invoke for:

- Pure statistics (mean, median, regression) — use pandas directly
- Time series forecasting
- Image or audio data
- Non-tabular data (free-form documents, PDFs)

## Prerequisites

The `semantic-analyzer` package must be installed and on PATH. Verify:

```bash
semantic-analyzer --version
```

If missing, install from the repo root:

```bash
pip install -e .
```

An API key must be available for at least one provider. Check:

```bash
env | grep -E "DEEPSEEK_API_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY"
```

If no key is set, ask the user which provider to use and for the key.

## Workflow

The skill is a 6-stage pipeline. Each stage has a clear input/output contract.
Never skip a stage. The first three stages (INSPECT, CLEAN, DESIGN) are
**mandatory** — they prevent the most common failure modes (running the LLM on
dirty data, designing an impossible task, etc.).

### Stage 1: INSPECT

Goal: understand the dataset before touching it.

```bash
semantic-analyzer info /path/to/user_data.csv
```

Output gives you:
- Total rows
- Column names
- Empty cell count
- Duplicate row count
- First 3 rows as a sample

**Decide**:
- Is the file too large? (>50k rows) → consider chunking
- Are there obvious data quality issues visible in the sample?
- Which columns contain the text the user wants analyzed?

**Report to user**: "I see N rows and M columns. The main text appears to be
in column X. I notice Y duplicates and Z empty cells. Proceeding to cleaning."

### Stage 2: CLEAN

Goal: remove noise, normalize text, ensure consistent structure.

The default cleaning config is:
- Drop exact duplicate rows
- Drop fully-empty rows
- Trim whitespace
- Unicode NFC normalization
- Collapse internal whitespace

For a dry-run that shows what cleaning would do (no LLM call):

```bash
semantic-analyzer run /path/to/user_data.csv "dummy" --dry-run --output /tmp/clean_preview.csv
```

If the user has specific cleaning needs (e.g., lowercase, fill missing, dedupe
by email only), ask before proceeding, then use flags:

```bash
# Examples
semantic-analyzer run data.csv "task" --no-dedupe --lowercase --fill-na "UNKNOWN"
```

For column-specific rules, edit `~/.config/semantic-analyzer/config.yaml` or
pass `--dedupe-subset email,name` (CLI flag for subset dedupe).

**Report to user**: "Removed X duplicates, Y empty rows. Cleaned file has N
rows. Proceeding to task design."

### Stage 3: DESIGN

Goal: write a clear, unambiguous task description for the LLM.

The task description is the most important variable. Vague tasks → bad
results. Use this template:

```
Extract [field_name_1] ([type/allowed_values]),
[field_name_2] ([type/allowed_values]),
...
and [field_name_N] ([type/allowed_values]).
```

**Rules**:
1. Use closed enumerations when possible (e.g., `Positive/Negative/Neutral` not `how does it feel`).
2. Specify units for numerics (e.g., `score (1-10)`, `confidence (0-1)`).
3. One field per concern — don't ask for both sentiment and topic in one field.
4. Match field count to data complexity: 2-5 fields for most use cases.
5. If the dataset has multi-language content, mention it: "text may be in English or Spanish".

**Examples of good task descriptions**:

```
# E-commerce reviews
"Extract sentiment (Positive/Negative/Neutral), sentiment_confidence (0-1),
detect_sarcasm (true/false), and main_complaint (short phrase or N/A)."

# Lead scoring
"Classify purchase_intent (High/Medium/Low), company_size (Startup/SMB/Enterprise),
budget_signal (Low/Medium/High), and lead_score (0-100)."

# Support tickets
"Identify topic (Billing/Technical/Account/Other), urgency (Low/Medium/High/Critical),
sentiment (Calm/Frustrated/Angry), and needs_escalation (true/false)."
```

**Pre-built templates** are available — list them with `semantic-analyzer tasks` and pick one if it fits.

**Report to user**: Show the task description. Ask: "Does this capture what
you want? I can adjust the fields, types, or value ranges."

### Stage 4: EXECUTE

Goal: run the analyzer with the right configuration.

For small datasets (< 5k rows):

```bash
semantic-analyzer run /path/to/data.csv "TASK_DESCRIPTION" \
    --output /path/to/results.csv \
    --output-format csv
```

For large datasets (> 5k rows), use chunking:

```bash
semantic-analyzer run /path/to/data.csv "TASK_DESCRIPTION" \
    --output /path/to/results.csv \
    --chunk-strategy rows \
    --chunk-size 500 \
    --resume
```

For local/offline processing (privacy-sensitive data):

```bash
# Make sure Ollama is running first
ollama pull llama3.2

semantic-analyzer run data.csv "TASK" --provider ollama
```

For deterministic results (recommended for production):

```bash
semantic-analyzer run data.csv "TASK" --max-workers 3   # slower but more stable
```

**Cost estimation**: before running on large data, estimate cost:

```python
# Average row is ~200 tokens input + 100 tokens output
# 10k rows = 2M input + 1M output
# DeepSeek: 2M * $0.27/M + 1M * $1.10/M = $1.64
# GPT-4o-mini: 2M * $0.15/M + 1M * $0.60/M = $0.90
# Claude Haiku: 2M * $0.80/M + 1M * $4.00/M = $5.60
```

Always show the user the cost estimate and ask for confirmation on large runs.

**Report to user**: Show the progress. On completion, show the summary:
"Processed N rows in M seconds. Total cost: $X. Output: /path/to/results.csv."

### Stage 5: INTERPRET

Goal: validate the output before reporting success.

Check the result file:

```bash
# Row count should match (or be slightly less if some failed)
wc -l /path/to/results.csv

# Quick distribution check
head -5 /path/to/results.csv
```

For each new column produced by the LLM, validate:

1. **No unexpected nulls**: > 5% nulls in a field usually means the LLM didn't understand the task. Re-run with a clearer prompt.
2. **Distribution sanity**: e.g., if you asked for sentiment and got 95% Positive, the task may be biased.
3. **Type consistency**: all values in a numeric column should be parseable as numbers.
4. **No `analysis_error` rows**: a high error rate (> 5%) means retries are failing. Check API key, rate limits, or simplify the task.

If something looks off, **stop and tell the user**. Don't paper over bad data.

### Stage 6: REPORT

Goal: deliver clear, actionable results to the user.

Structure your report:

1. **What was done**: "Processed N rows of [dataset description] using [provider/model]."
2. **Key findings**: 2-4 bullet points with specific numbers.
3. **Output file**: full path and format.
4. **Cost**: total tokens and USD.
5. **Caveats**: any issues encountered, rows that failed, etc.
6. **Next steps**: optional — what they could do next (visualize, drill down, re-run with different task).

Example:

> ## Analysis Complete
>
> Processed **1,247 reviews** with DeepSeek V3 in **42 seconds**. Cost: **$0.18**.
>
> **Key findings:**
> - 62% positive, 28% negative, 10% neutral
> - 14% of reviews contain detected sarcasm
> - Top complaint category: "shipping delay" (31% of negatives)
> - Lead quality is bimodal: enterprise (>500 seats) shows High intent, SMB is mixed
>
> Output: `/Users/.../analyzed_reviews.csv` (CSV with original columns + 4 new)
>
> **Caveats:** 8 rows failed (LLM returned malformed JSON). They're in the
> output with `analysis_error` filled in — you can filter them out.
>
> **Next steps:** Want me to drill into the sarcastic reviews, or run
> clustering on the complaints?

## Common pitfalls

1. **Don't run on raw data** — always inspect + clean first.
2. **Don't design vague tasks** — "analyze this" gets you nowhere.
3. **Don't ignore errors** — a 10% failure rate means something's wrong.
4. **Don't process PII with cloud LLMs** — use Ollama for sensitive data.
5. **Don't skip the cost estimate** on large runs.
6. **Don't trust the LLM blindly** — sample the output, check distributions.
7. **Don't commit `.env` or output files with PII** — use `.checkpoints/` and
   add the output paths to `.gitignore`.

## Helper scripts

The `scripts/` directory has standalone helpers you can use without invoking
the full skill:

- `inspect.py` — print dataset shape and column types
- `estimate_cost.py` — estimate cost before a run
- `validate_output.py` — sanity-check the result file

## Examples

### Example 1: Customer reviews

User: "I have a CSV of customer reviews. Can you tell me how people feel?"

```
1. INSPECT:    5000 rows, columns: id, review_text, rating, date
2. CLEAN:      47 duplicates, 0 empties → 4953 rows
3. DESIGN:     "Extract sentiment (Positive/Negative/Neutral),
                sentiment_confidence (0-1), sarcasm (true/false)."
4. EXECUTE:    semantic-analyzer run reviews.csv "..." --provider deepseek
               Result: 4953 rows in 1m 47s, $0.32
5. INTERPRET:  Distribution: 58% P, 32% N, 10% Neut. 12% sarcasm. Sensible.
6. REPORT:     See template above.
```

### Example 2: Lead scoring

User: "Process my sales leads and tell me which are hot."

```
1. INSPECT:    800 rows, columns: id, message, source, signup_date
2. CLEAN:      no duplicates, 3 empty messages → drop them → 797 rows
3. DESIGN:     "Classify purchase_intent (High/Medium/Low),
                company_size (Startup/SMB/Enterprise/Unknown),
                budget_signal (Low/Medium/High/Unknown),
                lead_score (0-100)."
4. EXECUTE:    semantic-analyzer run leads.csv "..." --provider openai --model gpt-4o-mini
               Result: 797 rows in 38s, $0.45
5. INTERPRET:  23% High intent. Reasonable for top-of-funnel leads.
6. REPORT:     Show top 10 high-intent leads with their scores.
```

### Example 3: Multi-language support tickets

User: "Triage these tickets, they're in English and German."

```
1. INSPECT:    2000 rows, columns: id, message, language
2. CLEAN:      5 empties → drop
3. DESIGN:     Task description includes: "Messages may be in English or German.
                Classify topic (Billing/Technical/Account/Other),
                urgency (Low/Medium/High/Critical),
                sentiment (Calm/Frustrated/Angry),
                needs_escalation (true/false)."
4. EXECUTE:    semantic-analyzer run tickets.csv "..." --chunk-size 200
5. INTERPRET:  Check that German tickets got reasonable classifications.
6. REPORT:     Break down by language.
```

## Anti-patterns (what NOT to do)

- ❌ Run the analyzer without inspecting first
- ❌ Use the same task description for vastly different datasets
- ❌ Trust the LLM on numbers (it can hallucinate scores)
- ❌ Skip the cost estimate on large runs
- ❌ Process PII with cloud LLMs without warning the user
- ❌ Forget to mention the output file path
- ❌ Hide failures — surface them in the report
- ❌ Re-run without fixing the root cause when results look bad
