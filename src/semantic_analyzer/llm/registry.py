"""LLM client registry."""

from __future__ import annotations

from semantic_analyzer.config import Config, Provider
from semantic_analyzer.exceptions import ConfigurationError
from semantic_analyzer.llm.base import BaseLLMClient


class LLMRegistry:
    """Registry of LLM provider factories."""

    _factories: dict[Provider, type[BaseLLMClient]] = {}

    @classmethod
    def register(cls, provider: Provider, factory: type[BaseLLMClient]) -> None:
        cls._factories[provider] = factory

    @classmethod
    def get(cls, provider: Provider) -> type[BaseLLMClient]:
        if provider not in cls._factories:
            raise ConfigurationError(f"No client registered for provider: {provider}")
        return cls._factories[provider]

    @classmethod
    def list_providers(cls) -> list[Provider]:
        return list(cls._factories.keys())


# Register built-in clients
def _register_defaults() -> None:
    from semantic_analyzer.llm.anthropic import AnthropicClient
    from semantic_analyzer.llm.openai_compat import OpenAICompatibleClient

    LLMRegistry.register(Provider.DEEPSEEK, OpenAICompatibleClient)
    LLMRegistry.register(Provider.OPENAI, OpenAICompatibleClient)
    LLMRegistry.register(Provider.OLLAMA, OpenAICompatibleClient)
    LLMRegistry.register(Provider.ANTHROPIC, AnthropicClient)


_register_defaults()


def get_client(config: Config) -> BaseLLMClient:
    """Build an LLM client from a Config.

    Args:
        config: Pipeline configuration.

    Returns:
        Configured client instance.

    Raises:
        ConfigurationError: If the provider is unknown or misconfigured.
    """
    client_cls = LLMRegistry.get(config.provider)
    provider_cfg = config.active_provider_config

    if config.provider != Provider.OLLAMA and not provider_cfg.api_key:
        raise ConfigurationError(
            f"API key is required for provider '{config.provider.value}'. "
            f"Set the {config.provider.value.upper()}_API_KEY environment variable."
        )

    return client_cls(
        api_key=provider_cfg.api_key,
        base_url=provider_cfg.base_url,
        model=provider_cfg.model,
        max_retries=config.max_retries,
    )
