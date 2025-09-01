"""OpenAI provider implementation."""

import os
from typing import Dict, Any, Optional
from openai import OpenAI
from .base import LLMProvider
from ..exceptions import LLMProviderError


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider with JSON mode support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo", **config):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
            model: Model name to use (default: gpt-4-turbo)
            **config: Additional configuration
        """
        super().__init__(api_key=api_key, model=model, **config)
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if not self.api_key:
            raise LLMProviderError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
    
    def _get_client(self) -> OpenAI:
        """Get or create OpenAI client."""
        if self.client is None:
            self.client = OpenAI(api_key=self.api_key)
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
        Generate structured data using OpenAI GPT.
        
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
                "response_format": {"type": "json_object"}  # Enable JSON mode
            }
            
            if max_tokens:
                request_params["max_tokens"] = max_tokens
            
            # Make API call
            response = client.chat.completions.create(**request_params)
            
            # Extract content
            if not response.choices:
                raise LLMProviderError("No response choices returned from OpenAI")
            
            content = response.choices[0].message.content
            if not content:
                raise LLMProviderError("Empty response content from OpenAI")
            
            return content.strip()
            
        except Exception as e:
            if isinstance(e, LLMProviderError):
                raise
            
            error_msg = str(e)
            if "api_key" in error_msg.lower():
                raise LLMProviderError(
                    "OpenAI API authentication failed. Check your API key."
                ) from e
            elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
                raise LLMProviderError(
                    "OpenAI API rate limit or quota exceeded. Try again later."
                ) from e
            elif "model" in error_msg.lower():
                raise LLMProviderError(
                    f"OpenAI model '{self.model}' not available or not supported."
                ) from e
            else:
                raise LLMProviderError(
                    f"OpenAI API error: {error_msg}"
                ) from e
    
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            LLMProviderError: If configuration is invalid
        """
        if not self.api_key:
            raise LLMProviderError("OpenAI API key is required")
        
        if not self.model:
            raise LLMProviderError("Model name is required")
        
        # Validate model supports JSON mode
        json_mode_models = [
            "gpt-4-turbo",
            "gpt-4-turbo-preview", 
            "gpt-4-0125-preview",
            "gpt-4-1106-preview",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0125"
        ]
        
        if not any(supported in self.model for supported in json_mode_models):
            raise LLMProviderError(
                f"Model '{self.model}' does not support JSON mode. "
                f"Supported models: {', '.join(json_mode_models)}"
            )
        
        try:
            # Test API connection with a simple request
            client = self._get_client()
            client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            raise LLMProviderError(
                f"Failed to validate OpenAI configuration: {str(e)}"
            ) from e
    
    @property
    def name(self) -> str:
        """Provider name for identification."""
        return "openai"
    
    @property
    def supports_json_mode(self) -> bool:
        """Whether this provider supports structured JSON output."""
        return True