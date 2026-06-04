"""Retry utilities with exponential backoff."""

from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable, TypeVar

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random_exponential,
)

from semantic_analyzer.exceptions import LLMError, LLMRateLimitError, LLMTimeoutError

T = TypeVar("T")

# Exceptions that should trigger a retry
RETRYABLE_EXCEPTIONS: tuple[type[BaseException], ...] = (
    LLMRateLimitError,
    LLMTimeoutError,
    LLMError,
    ConnectionError,
    TimeoutError,
)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator: sync retry with exponential backoff."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            wait = wait_random_exponential(min=base_delay, max=max_delay) if jitter else wait_exponential(multiplier=base_delay, max=max_delay)
            for attempt in Retrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait,
                retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
                reraise=True,
            ):
                with attempt:
                    return func(*args, **kwargs)
            # Unreachable, but type checkers want a return
            raise RuntimeError("retry decorator: no result returned")  # pragma: no cover

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator: async retry with exponential backoff."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            wait = wait_random_exponential(min=base_delay, max=max_delay) if jitter else wait_exponential(multiplier=base_delay, max=max_delay)
            for attempt in AsyncRetrying(
                stop=stop_after_attempt(max_attempts),
                wait=wait,
                retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
                reraise=True,
            ):
                with attempt:
                    return await func(*args, **kwargs)
            raise RuntimeError("async_retry decorator: no result returned")  # pragma: no cover

        return wrapper

    return decorator
