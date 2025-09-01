"""Provider registry for managing LLM providers."""

from typing import Dict, Type, Any
from .base import LLMProvider
from ..exceptions import WeaverError


class ProviderRegistry:
    """Registry for LLM providers."""
    
    def __init__(self):
        self._providers: Dict[str, Type[LLMProvider]] = {}
        self._instances: Dict[str, LLMProvider] = {}
    
    def register(self, name: str, provider_class: Type[LLMProvider]) -> None:
        """
        Register a provider class.
        
        Args:
            name: Provider name
            provider_class: Provider class that inherits from LLMProvider
        """
        if not issubclass(provider_class, LLMProvider):
            raise WeaverError(f"Provider {name} must inherit from LLMProvider")
        
        self._providers[name] = provider_class
    
    def get_provider(self, name: str, **config: Any) -> LLMProvider:
        """
        Get a provider instance with configuration.
        
        Args:
            name: Provider name
            **config: Configuration parameters for the provider
            
        Returns:
            Configured provider instance
            
        Raises:
            WeaverError: If provider is not registered
        """
        if name not in self._providers:
            available = ", ".join(self._providers.keys())
            raise WeaverError(
                f"Provider '{name}' not found. Available providers: {available}"
            )
        
        # Create a cache key based on name and config
        cache_key = f"{name}:{hash(frozenset(config.items()) if config else frozenset())}"
        
        if cache_key not in self._instances:
            provider_class = self._providers[name]
            instance = provider_class(**config)
            instance.validate_config()
            self._instances[cache_key] = instance
        
        return self._instances[cache_key]
    
    def list_providers(self) -> list[str]:
        """List all registered provider names."""
        return list(self._providers.keys())
    
    def clear_cache(self) -> None:
        """Clear all cached provider instances."""
        self._instances.clear()


# Global registry instance
registry = ProviderRegistry()