"""Weaver model management using Pydantic AI models with providers."""

import os
from typing import Union, Optional, Any
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel as GeminiModel

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from .exceptions import WeaverError

try:
    from pydantic_ai.models.groq import GroqModel
    from pydantic_ai.providers.groq import GroqProvider
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    from pydantic_ai.providers.google import GoogleProvider
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

# Type for all supported models
WeaverModel = Union[OpenAIChatModel, AnthropicModel, GeminiModel]

# Model configuration mapping provider to model class
MODEL_CONFIG = {
    "openai": {
        "model_class": OpenAIChatModel,
        "provider_class": OpenAIProvider,
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4-turbo",
        "provider_param": "openai"  # For OpenAIChatModel provider parameter
    },
    "anthropic": {
        "model_class": AnthropicModel,
        "provider_class": AnthropicProvider,
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-3-5-sonnet-20241022",
        "provider_param": None  # AnthropicModel uses provider instance directly
    },
    "gemini": {
        "model_class": GeminiModel,
        "provider_class": None,  # Gemini uses API key directly
        "env_key": "GEMINI_API_KEY",
        "default_model": "gemini-1.5-pro",
        "provider_param": None
    },
    "openrouter": {
        "model_class": OpenAIChatModel,  # OpenRouter uses OpenAI-compatible interface
        "provider_class": OpenRouterProvider,
        "env_key": "OPENROUTER_API_KEY", 
        "default_model": "google/gemini-2.5-flash-lite",
        "provider_param": None  # Provider instance passed directly
    }
}

# Add optional providers if available
if GROQ_AVAILABLE:
    MODEL_CONFIG["groq"] = {
        "model_class": GroqModel,
        "provider_class": GroqProvider,
        "env_key": "GROQ_API_KEY",
        "default_model": "llama-3.1-70b-versatile",
        "provider_param": None
    }

if GOOGLE_AVAILABLE:
    MODEL_CONFIG["google"] = {
        "model_class": GeminiModel,  # Use GeminiModel for Google
        "provider_class": GoogleProvider,
        "env_key": "GOOGLE_AI_API_KEY",
        "default_model": "gemini-1.5-pro",
        "provider_param": None
    }


def create_model(
    provider_name: str,
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> WeaverModel:
    """
    Create a Pydantic AI model with the appropriate provider.
    
    Args:
        provider_name: Provider name (openai, anthropic, gemini, openrouter, etc.)
        model_name: Model name (uses default if not specified)
        api_key: API key (uses environment variable if not specified)
        **kwargs: Additional model parameters
        
    Returns:
        Configured Pydantic AI model instance ready for Agent
        
    Raises:
        WeaverError: If provider not supported or configuration invalid
    """
    if provider_name not in MODEL_CONFIG:
        available = ", ".join(MODEL_CONFIG.keys())
        raise WeaverError(f"Provider '{provider_name}' not supported. Available: {available}")
    
    config = MODEL_CONFIG[provider_name]
    model_class = config["model_class"]
    provider_class = config["provider_class"]
    
    # Get API key
    final_api_key = api_key or os.getenv(config["env_key"])
    if not final_api_key:
        raise WeaverError(f"API key required for {provider_name}. Set {config['env_key']} or pass api_key parameter")
    
    # Get model name
    final_model_name = model_name or config["default_model"]
    
    try:
        # Create model based on provider requirements
        if provider_name == "openai":
            # OpenAI uses provider parameter as string
            return model_class(
                model_name=final_model_name,
                provider="openai",
                **kwargs
            )
        
        elif provider_name == "anthropic":
            # Anthropic uses provider instance
            provider = provider_class(api_key=final_api_key)
            return model_class(
                model_name=final_model_name,
                provider=provider,
                **kwargs
            )
        
        elif provider_name == "gemini":
            # Gemini uses API key directly
            return model_class(
                model_name=final_model_name,
                api_key=final_api_key,
                **kwargs
            )
        
        elif provider_name == "openrouter":
            # OpenRouter uses OpenAIChatModel with OpenRouterProvider
            provider = provider_class(api_key=final_api_key)
            return OpenAIChatModel(
                model_name=final_model_name,
                provider=provider,
                **kwargs
            )
        
        elif provider_name == "groq" and GROQ_AVAILABLE:
            # Groq uses provider instance
            provider = provider_class(api_key=final_api_key)
            return GroqModel(
                model_name=final_model_name,
                provider=provider,
                **kwargs
            )
        
        else:
            # Generic case for other providers
            if provider_class:
                provider = provider_class(api_key=final_api_key)
                return model_class(
                    model_name=final_model_name,
                    provider=provider,
                    **kwargs
                )
            else:
                return model_class(
                    model_name=final_model_name,
                    api_key=final_api_key,
                    **kwargs
                )
                
    except Exception as e:
        raise WeaverError(f"Failed to create {provider_name} model: {str(e)}") from e


def get_available_providers() -> list[str]:
    """Get list of available providers."""
    return list(MODEL_CONFIG.keys())


def get_default_model(provider_name: str) -> str:
    """Get default model for a provider."""
    if provider_name not in MODEL_CONFIG:
        raise WeaverError(f"Provider '{provider_name}' not found")
    return MODEL_CONFIG[provider_name]["default_model"]


def get_model_info(provider_name: str) -> dict[str, Any]:
    """Get information about a provider's model configuration."""
    if provider_name not in MODEL_CONFIG:
        raise WeaverError(f"Provider '{provider_name}' not found")
    
    config = MODEL_CONFIG[provider_name]
    return {
        "name": provider_name,
        "model_class": config["model_class"].__name__,
        "provider_class": config["provider_class"].__name__ if config["provider_class"] else None,
        "default_model": config["default_model"],
        "env_key": config["env_key"],
        "available": config["env_key"] in os.environ
    }