"""Core Weaver class for generating test data."""

from typing import Type, Union, List, Optional, Dict, Any
from pydantic import BaseModel

from .dependency_resolver import DependencyResolver
from .prompt_builder import PromptBuilder
from .data_generator import DataGenerator
from ..models import create_model, get_default_model
from ..exceptions import WeaverError


class Weaver:
    """Main class for generating realistic test data using LLMs.
    
    This is the simplified, modular version of Weaver that delegates
    specialized tasks to dedicated modules.
    """
    
    def __init__(
        self,
        provider: Union[str, object] = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **config
    ):
        """
        Initialize Weaver with Pydantic AI provider.
        
        Args:
            provider: Provider name or Pydantic AI provider instance
            api_key: API key for the provider (ignored if provider is instance)
            model: Model name to use
            **config: Additional provider configuration
        """
        self.config = config
        
        # Handle both provider names and model instances
        if isinstance(provider, str):
            # Create model from provider name
            self.model_name = model or get_default_model(provider)
            self.model = create_model(
                provider_name=provider,
                model_name=self.model_name,
                api_key=api_key,
                **config
            )
            self.provider_name = provider
        else:
            # Use provided model instance (assuming it's a Pydantic AI model)
            self.model = provider
            self.model_name = model or getattr(provider, 'model_name', 'unknown')
            self.provider_name = getattr(provider, '__class__', type(provider)).__name__.lower().replace('model', '')
        
        # Initialize specialized modules
        self._data_generator = DataGenerator(self.model, self.model_name, self.provider_name)
    
    def generate(
        self,
        model: Union[Type[BaseModel], Dict[str, Type[BaseModel]], List[Type[BaseModel]]],
        prompt: Union[str, Dict[str, str]] = "",
        count: int = 1,
        **options
    ) -> Union[BaseModel, List[BaseModel], Dict[str, Union[BaseModel, List[BaseModel]]]]:
        """
        Universal generate method that handles all scenarios intelligently.
        
        Args:
            model: Single model, dict of models, or list of models
            prompt: Single prompt, dict of prompts, or default prompt
            count: Number of instances to generate
            **options: Additional options (realistic=True, diverse=True, etc.)

        Returns:
            Generated data matching input structure
        """
        
        try:
            # Scenario 1: Single model
            if isinstance(model, type) and issubclass(model, BaseModel):
                return self._generate_single(model, prompt, count, **options)
            
            # Scenario 2: Multiple models (dict or list)
            elif isinstance(model, (dict, list)):
                return self._generate_multiple(model, prompt, count, **options)
            
            else:
                raise WeaverError(f"Invalid model type: {type(model)}")
                
        except Exception as e:
            raise WeaverError(f"Generation failed: {str(e)}") from e
    
    def _generate_single(
        self, 
        model: Type[BaseModel], 
        prompt: str, 
        count: int, 
        **options
    ) -> Union[BaseModel, List[BaseModel]]:
        """Generate data for a single model with auto-dependency detection."""
        
        # Auto-detect if this model has dependencies that need to be generated first
        dependencies = DependencyResolver.auto_detect_dependencies(model)
        
        if dependencies:
            # This model has dependencies - generate them first
            dependency_models = {}
            dependency_prompts = {}
            
            for dep_model_class in dependencies:
                dep_name = dep_model_class.__name__.lower()
                dependency_models[dep_name] = dep_model_class
                dependency_prompts[dep_name] = PromptBuilder.infer_prompt(dep_model_class, options)
            
            # Add the main model
            main_name = model.__name__.lower()
            dependency_models[main_name] = model
            dependency_prompts[main_name] = PromptBuilder.enhance_prompt(prompt, model, options)
            
            # Generate all related data
            results = self._data_generator.generate_related_data(
                dependency_models, dependency_prompts, count
            )
            
            # Return only the requested model's data
            return results[main_name]
        else:
            # No dependencies - generate directly
            enhanced_prompt = PromptBuilder.enhance_prompt(prompt, model, options)
            return self._data_generator.generate_independent(model, enhanced_prompt, count)
    
    def _generate_multiple(
        self, 
        models: Union[Dict[str, Type[BaseModel]], List[Type[BaseModel]]], 
        prompts: Union[str, Dict[str, str]], 
        count: int, 
        **options
    ) -> Dict[str, Union[BaseModel, List[BaseModel]]]:
        """Generate data for multiple models with automatic relationship detection."""
        
        # Normalize inputs using utility modules
        models_dict = DependencyResolver.normalize_models_input(models)
        model_names = list(models_dict.keys())
        prompts_dict = PromptBuilder.normalize_prompts_input(prompts, model_names, options)
        
        # Auto-enhance prompts
        for name, model_class in models_dict.items():
            if name in prompts_dict:
                prompts_dict[name] = PromptBuilder.enhance_prompt(
                    prompts_dict[name], model_class, options
                )
        
        return self._data_generator.generate_related_data(models_dict, prompts_dict, count)
    
    # Legacy and utility methods
    @property
    def provider_name_property(self) -> str:
        """Get the name of the current provider."""
        return self.provider_name
    
    @property
    def provider_info(self) -> dict:
        """Get information about the current provider."""
        return {
            "name": self.provider_name,
            "model": self.model_name,
            "config": self.config
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