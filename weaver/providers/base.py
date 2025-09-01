"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, **config: Any):
        """Initialize the provider with configuration."""
        self.config = config
    
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate structured data using the LLM.
        
        Args:
            system_prompt: System prompt containing instructions and schema
            user_prompt: User's natural language description
            schema: JSON Schema for structured output
            temperature: Generation temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated JSON string that should match the schema
            
        Raises:
            LLMProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate the provider configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            LLMProviderError: If configuration is invalid
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for identification."""
        pass
    
    @property
    @abstractmethod
    def supports_json_mode(self) -> bool:
        """Whether this provider supports structured JSON output."""
        pass