"""LLM providers for Weaver."""

from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .openrouter_provider import OpenRouterProvider
from .registry import registry, ProviderRegistry

# Register built-in providers
registry.register("openai", OpenAIProvider)
registry.register("openrouter", OpenRouterProvider)

__all__ = [
    "LLMProvider",
    "OpenAIProvider",
    "OpenRouterProvider",
    "registry",
    "ProviderRegistry",
]