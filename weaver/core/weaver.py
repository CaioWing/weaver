"""Core Weaver class for generating test data."""

from typing import Type, Union, List, Optional
from pydantic import BaseModel

from .schema_converter import SchemaConverter
from .validator import ResponseValidator
from ..providers import registry, LLMProvider
from ..exceptions import WeaverError, ValidationError


class Weaver:
    """Main class for generating realistic test data using LLMs."""
    
    def __init__(
        self,
        provider: Optional[Union[str, LLMProvider]] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **config
    ):
        """
        Initialize Weaver with LLM provider configuration.
        
        Args:
            provider: Provider name or instance (default: "openai")
            api_key: API key for the provider
            model: Model name to use
            **config: Additional provider configuration
        """
        self.config = config
        
        # Set up provider
        if isinstance(provider, LLMProvider):
            self.provider = provider
        else:
            provider_name = provider or "openai"
            provider_config = {
                "api_key": api_key,
                "model": model or self._get_default_model(provider_name),
                **config
            }
            # Remove None values
            provider_config = {k: v for k, v in provider_config.items() if v is not None}
            
            try:
                self.provider = registry.get_provider(provider_name, **provider_config)
            except Exception as e:
                raise WeaverError(f"Failed to initialize provider '{provider_name}': {str(e)}") from e
    
    def generate(
        self,
        model: Type[BaseModel],
        prompt: str,
        count: int = 1,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
    ) -> Union[BaseModel, List[BaseModel]]:
        """
        Generate test data based on a Pydantic model and natural language prompt.
        
        Args:
            model: Pydantic model class to generate data for
            prompt: Natural language description of the desired data
            count: Number of instances to generate (default: 1)
            temperature: Generation temperature 0.0-1.0 (default: 0.1)
            max_tokens: Maximum tokens to generate
            max_retries: Maximum number of retries on validation failure
            
        Returns:
            Single model instance if count=1, otherwise list of instances
            
        Raises:
            WeaverError: If generation fails
            ValidationError: If validation fails after all retries
        """
        try:
            # Convert Pydantic model to JSON Schema
            schema = SchemaConverter.convert_to_json_schema(model)
            
            # Create system prompt with schema
            system_prompt = SchemaConverter.create_system_prompt(schema, model.__name__)
            
            # Modify user prompt for multiple instances
            if count > 1:
                user_prompt = f"Generate {count} different instances of the following: {prompt}"
                # Wrap schema in array for multiple instances
                array_schema = {
                    "type": "array",
                    "items": schema,
                    "minItems": count,
                    "maxItems": count
                }
                system_prompt = SchemaConverter.create_system_prompt(array_schema, model.__name__)
            else:
                user_prompt = prompt
            
            # Generate with retries
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    # Call LLM provider
                    response = self.provider.generate(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                        schema=schema,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                    # Validate and parse response
                    result = ResponseValidator.validate_and_parse(
                        response=response,
                        model=model,
                        allow_partial=False
                    )
                    
                    # Result is always a list now, handle based on count requested
                    if not isinstance(result, list):
                        raise ValidationError("Internal error: expected list from validator")
                    
                    if count == 1:
                        # User wanted single instance, return just the first item
                        if len(result) >= 1:
                            return result[0]
                        else:
                            raise ValidationError("No valid instances generated")
                    else:
                        # User wanted multiple instances
                        if len(result) == count:
                            return result
                        elif len(result) < count:
                            raise ValidationError(
                                f"Expected {count} instances, got {len(result)}"
                            )
                        else:
                            return result[:count]  # Trim to requested count
                    
                except ValidationError as e:
                    last_error = e
                    if attempt < max_retries:
                        # Modify prompt for retry
                        user_prompt = f"{prompt} (Attempt {attempt + 2}: Please ensure valid JSON format)"
                        continue
                    else:
                        break
            
            # If we get here, all retries failed
            if last_error:
                raise last_error
            else:
                raise WeaverError("Generation failed after all retries")
                
        except (WeaverError, ValidationError):
            raise
        except Exception as e:
            raise WeaverError(f"Unexpected error during generation: {str(e)}") from e
    
    def _get_default_model(self, provider_name: str) -> str:
        """Get default model for a provider."""
        defaults = {
            "openai": "gpt-4-turbo",
            "openrouter": "openai/gpt-4-turbo",
        }
        return defaults.get(provider_name, "gpt-4-turbo")
    
    @property
    def provider_name(self) -> str:
        """Get the name of the current provider."""
        return self.provider.name
    
    @property
    def provider_info(self) -> dict:
        """Get information about the current provider."""
        return {
            "name": self.provider.name,
            "supports_json_mode": self.provider.supports_json_mode,
            "config": getattr(self.provider, "config", {})
        }
    
    @staticmethod
    def format_results(result: Union[BaseModel, List[BaseModel]], format: str = "summary") -> str:
        """
        Format generation results for display.
        
        Args:
            result: Single model instance or list of instances
            format: "summary", "json", or "detailed"
            
        Returns:
            Formatted string representation
        """
        if isinstance(result, list):
            if format == "json":
                return "[\n" + ",\n".join(
                    item.model_dump_json(indent=2) for item in result
                ) + "\n]"
            elif format == "detailed":
                output = [f"Generated {len(result)} instances:\n"]
                for i, item in enumerate(result, 1):
                    output.append(f"=== Instance {i} ===")
                    output.append(item.model_dump_json(indent=2))
                return "\n".join(output)
            else:  # summary
                return f"Generated {len(result)} instances of {result[0].__class__.__name__}"
        else:
            if format == "json":
                return result.model_dump_json(indent=2)
            elif format == "detailed":
                return f"Generated 1 instance:\n{result.model_dump_json(indent=2)}"
            else:  # summary
                return f"Generated 1 instance of {result.__class__.__name__}"