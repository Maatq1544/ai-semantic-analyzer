"""Tests for prompt templates."""

from semantic_analyzer.prompts.templates import (
    build_system_prompt,
    build_user_prompt,
    get_default_task,
)


def test_system_prompt_for_json_mode() -> None:
    prompt = build_system_prompt("deepseek")
    assert "JSON" in prompt


def test_system_prompt_for_anthropic() -> None:
    prompt = build_system_prompt("anthropic")
    assert "JSON" in prompt
    assert "no markdown" in prompt.lower()


def test_user_prompt() -> None:
    row = {"name": "Alice", "review": "Great!"}
    columns = ["name", "review"]
    prompt = build_user_prompt(row, columns, "Classify sentiment")
    assert "Classify sentiment" in prompt
    assert "Alice" in prompt
    assert "Great!" in prompt
    assert "name:" in prompt
    assert "review:" in prompt


def test_default_task() -> None:
    task = get_default_task("sentiment")
    assert task is not None
    assert "sentiment" in task.lower()


def test_unknown_task() -> None:
    assert get_default_task("nonexistent") is None
