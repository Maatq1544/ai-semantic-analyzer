"""Prompt templates for the analyzer pipeline."""

from __future__ import annotations

from typing import Any

# Default system prompt for JSON-mode providers (OpenAI/DeepSeek/Ollama)
SYSTEM_PROMPT_JSON = """You are a precise data analyst. You analyze tabular data row-by-row and return STRICTLY a flat JSON object.

RULES:
1. Return ONLY a flat JSON object — no markdown, no explanations, no preamble.
2. Keys must correspond exactly to the data points requested in the TASK.
3. Do NOT include nested objects unless explicitly asked.
4. If data is missing or unclear for a specific point, use "N/A" (string) or null.
5. Be concise. Use short values: words, short phrases, or 0-1 decimals.
6. Do not include fields not requested in the TASK.
"""

# System prompt for non-JSON-mode providers (Anthropic Claude)
SYSTEM_PROMPT_NATURAL = """You are a precise data analyst. You analyze tabular data row-by-row.

For each row you will be given:
- A task description (the data points to extract)
- The row contents

You MUST respond with a flat JSON object that exactly matches the requested data points.

Rules:
- No markdown fences (no ```json ... ```)
- No explanations or preamble
- Flat structure only (no nested objects unless explicitly asked)
- Use "N/A" or null for missing values
- Be concise: short words/phrases for text fields, 0-1 decimals for scores
"""


def build_system_prompt(provider: str) -> str:
    """Return the appropriate system prompt for the provider."""
    if provider in {"anthropic"}:
        return SYSTEM_PROMPT_NATURAL
    return SYSTEM_PROMPT_JSON


def build_user_prompt(
    row: dict[str, Any], columns: list[str], task_description: str
) -> str:
    """Build the user prompt for a single row.

    The row contents are formatted as a labeled block, making it explicit
    to the LLM which column is which.
    """
    row_lines = "\n".join(f"  - {col}: {row.get(col, '')}" for col in columns if col in row)

    return f"""TASK:
{task_description}

ROW TO ANALYZE:
{row_lines}

REQUIREMENTS:
- Return ONLY a flat JSON object.
- Keys must correspond to the data points in the TASK.
- Use "N/A" for missing/unclear values.
- No markdown, no explanations, no nested objects.
"""


# A handful of pre-built task templates for common use cases.
DEFAULT_TASKS: dict[str, str] = {
    "sentiment": (
        "Extract sentiment (Positive/Negative/Neutral), "
        "sentiment_confidence (0-1), and detect sarcasm (true/false)."
    ),
    "lead_scoring": (
        "Identify purchase_intent (High/Medium/Low), "
        "company_size (Startup/SMB/Enterprise), "
        "budget_signal (Low/Medium/High), "
        "and lead_score (0-100)."
    ),
    "ticket_classification": (
        "Classify topic (one of: Billing, Technical, Account, Other), "
        "urgency (Low/Medium/High/Critical), "
        "sentiment (Calm/Frustrated/Angry), "
        "and needs_escalation (true/false)."
    ),
    "review_analysis": (
        "Extract sentiment (Positive/Negative/Neutral), "
        "mentioned_features (comma-separated list), "
        "pain_points (comma-separated list), "
        "and overall_score (1-5)."
    ),
}


def get_default_task(name: str) -> str | None:
    """Return a default task description by name, or None if not found."""
    return DEFAULT_TASKS.get(name)
