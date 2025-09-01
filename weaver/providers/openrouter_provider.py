"""OpenRouter provider implementation for accessing multiple LLM models."""

import os
from typing import Dict, Any, Optional
from openai import OpenAI
from .base import LLMProvider
from ..exceptions import LLMProviderError


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider with access to multiple LLM models."""
    
    # Models that support JSON mode or structured output
    JSON_MODE_MODELS = {
        # OpenAI models
        "openai/gpt-4-turbo",
        "openai/gpt-4-turbo-preview", 
        "openai/gpt-4-0125-preview",
        "openai/gpt-4-1106-preview",
        "openai/gpt-3.5-turbo-1106",
        "openai/gpt-3.5-turbo-0125",
        # Anthropic models (structured prompting)
        "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-haiku",
        "anthropic/claude-3.5-sonnet",
        # Google models
        "google/gemini-pro-1.5",
        "google/gemini-pro",
    }
    
    # Default models by provider
    DEFAULT_MODELS = {
        "openai": "openai/gpt-4-turbo",
        "anthropic": "anthropic/claude-3.5-sonnet",
        "google": "google/gemini-pro-1.5",
        "meta": "meta-llama/llama-3.1-8b-instruct",
    }
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        model: str = "openai/gpt-4-turbo",
        base_url: str = "https://openrouter.ai/api/v1",
        **config
    ):
        """
        Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key (if not provided, uses OPENROUTER_API_KEY env var)
            model: Model name to use (default: openai/gpt-4-turbo)
            base_url: OpenRouter API base URL
            **config: Additional configuration
        """
        super().__init__(api_key=api_key, model=model, base_url=base_url, **config)
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self.base_url = base_url
        self.client = None
        
        # OpenRouter specific headers
        self.extra_headers = {
            "HTTP-Referer": config.get("http_referer", "https://weaver.dev"),
            "X-Title": config.get("x_title", "Weaver Data Generator"),
        }
        
        if not self.api_key:
            raise LLMProviderError(
                "OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable "
                "or pass api_key parameter. Get your key at: https://openrouter.ai/keys"
            )
    
    def _get_client(self) -> OpenAI:
        """Get or create OpenRouter client."""
        if self.client is None:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                default_headers=self.extra_headers
            )
        return self.client
    
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate structured data using OpenRouter.
        
        Args:
            system_prompt: System prompt with schema instructions
            user_prompt: User's natural language description
            schema: JSON Schema for structured output
            temperature: Generation temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated JSON string
            
        Raises:
            LLMProviderError: If generation fails
        """
        try:
            client = self._get_client()
            
            # Prepare messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Prepare request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            # Add JSON mode for supported models
            if self._supports_json_mode():
                request_params["response_format"] = {"type": "json_object"}
            else:
                # For models without JSON mode, enhance the prompt
                enhanced_system = f"{system_prompt}\n\nIMPORTANT: Respond with ONLY valid JSON, no additional text or explanation."
                messages[0]["content"] = enhanced_system
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # Make API call
            response = client.chat.completions.create(**request_params)
            
            # Extract content
            if not response.choices:
                raise LLMProviderError("No response choices returned from OpenRouter")
            
            content = response.choices[0].message.content
            if not content:
                raise LLMProviderError("Empty response content from OpenRouter")
            
            return content.strip()
            
        except Exception as e:
            if isinstance(e, LLMProviderError):
                raise
            
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                raise LLMProviderError(
                    "OpenRouter API authentication failed. Check your API key."
                ) from e
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise LLMProviderError(
                    "OpenRouter API rate limit or quota exceeded. Try again later."
                ) from e
            elif "model" in error_msg.lower():
                available_models = ", ".join(list(self.DEFAULT_MODELS.values())[:5])
                raise LLMProviderError(
                    f"OpenRouter model '{self.model}' not available. "
                    f"Try: {available_models}"
                ) from e
            else:
                raise LLMProviderError(
                    f"OpenRouter API error: {error_msg}"
                ) from e
    
    def _supports_json_mode(self) -> bool:
        """Check if current model supports JSON mode."""
        return self.model in self.JSON_MODE_MODELS
    
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            LLMProviderError: If configuration is invalid
        """
        if not self.api_key:
            raise LLMProviderError("OpenRouter API key is required")
        
        if not self.model:
            raise LLMProviderError("Model name is required")
        
        try:
            # Test API connection with a simple request
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                # Provide helpful model suggestions
                provider_prefix = self.model.split('/')[0] if '/' in self.model else "openai"
                suggested = self.DEFAULT_MODELS.get(provider_prefix, "openai/gpt-4-turbo")
                raise LLMProviderError(
                    f"Model '{self.model}' not found on OpenRouter. "
                    f"Try '{suggested}' or check https://openrouter.ai/models"
                ) from e
            else:
                raise LLMProviderError(
                    f"Failed to validate OpenRouter configuration: {error_msg}"
                ) from e
    
    @property
    def name(self) -> str:
        """Provider name for identification."""
        return "openrouter"
    
    @property
    def supports_json_mode(self) -> bool:
        """Whether this provider supports structured JSON output."""
        return self._supports_json_mode()
    
    @classmethod
    def get_available_models(cls) -> Dict[str, list]:
        """Get categorized list of popular models available on OpenRouter."""
        return {
            "openai": [
                "openai/gpt-4-turbo",
                "openai/gpt-4",
                "openai/gpt-3.5-turbo",
            ],
            "anthropic": [
                "anthropic/claude-3.5-sonnet",
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "anthropic/claude-3-haiku",
            ],
            "google": [
                "google/gemini-pro-1.5",
                "google/gemini-pro",
            ],
            "meta": [
                "meta-llama/llama-3.1-405b-instruct",
                "meta-llama/llama-3.1-70b-instruct",
                "meta-llama/llama-3.1-8b-instruct",
            ],
            "mistral": [
                "mistralai/mixtral-8x7b-instruct",
                "mistralai/mistral-7b-instruct",
            ]
        }
    
    @classmethod
    def get_recommended_model(cls, use_case: str = "general") -> str:
        """Get recommended model for specific use case."""
        recommendations = {
            "general": "openai/gpt-4-turbo",
            "fast": "openai/gpt-3.5-turbo",
            "creative": "anthropic/claude-3.5-sonnet", 
            "code": "openai/gpt-4-turbo",
            "analysis": "anthropic/claude-3-opus",
            "budget": "meta-llama/llama-3.1-8b-instruct",
        }
        return recommendations.get(use_case, "openai/gpt-4-turbo")