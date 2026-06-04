# Dataset Processor Skill

A Claude skill that walks an AI agent through the full workflow of taking a
user's raw dataset and producing structured LLM-analyzed output using the
[AI Semantic Analyzer](https://github.com/Maatq1544/ai-semantic-analyzer).

## What it does

1. **INSPECT** — reads the user's file, summarizes structure and quality
2. **CLEAN** — applies configurable data cleaning (dedupe, normalize, etc.)
3. **DESIGN** — co-designs the LLM task description with the user
4. **EXECUTE** — runs the analyzer with cost estimation
5. **INTERPRET** — validates the output and catches common failure modes
6. **REPORT** — delivers a clear, actionable summary

## Installation

This skill lives inside the AI Semantic Analyzer repo. To use it in another
project, copy `SKILL.md` to your Claude skills directory:

```bash
# As a user-level skill
cp skills/dataset-processor/SKILL.md ~/.claude/skills/dataset-processor/SKILL.md

# Or in a project
cp -r skills/dataset-processor /path/to/your/project/.claude/skills/
```

## Usage

Once installed, the skill activates when the user shares a data file and asks
for analysis. Example invocations:

- "Analyze this CSV of customer reviews"
- "Process my lead list and tell me which are hot"
- "Classify these support tickets by topic and urgency"
- "Score sentiment in this dataset"

The skill assumes the `semantic-analyzer` CLI is installed and on PATH.

## Helper Scripts

Three standalone scripts for stages of the workflow:

| Script | Purpose | Stage |
|---|---|---|
| `scripts/inspect.py` | Quick file inspection | INSPECT |
| `scripts/estimate_cost.py` | Cost estimation | EXECUTE |
| `scripts/validate_output.py` | Output validation | INTERPRET |

Run them directly:

```bash
python scripts/inspect.py data.csv
python scripts/estimate_cost.py data.csv --model deepseek-chat
python scripts/validate_output.py analyzed_data.csv
```

## Example session

```
USER: "I have a CSV of customer reviews. Can you tell me how people feel?"

AGENT (with skill):
  → Calls inspect.py
  → Reports: 5000 rows, columns: id, review, rating, date
  → Suggests: "Remove duplicates? Lowercase?"
  → Designs task: "Extract sentiment (Positive/Negative/Neutral),
                   sentiment_confidence (0-1), sarcasm (true/false)."
  → Asks for approval
  → Runs: semantic-analyzer run reviews.csv "..." --provider deepseek
  → Validates output
  → Reports: "62% positive, 28% negative, 10% neutral. 12% sarcasm detected.
              Top complaint: shipping delay. Output at /path/to/analyzed.csv"
```

## License

MIT — same as the parent project.
