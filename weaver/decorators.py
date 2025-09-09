"""Decorators and utilities to make Weaver more intuitive."""

from typing import Type, Dict, Any, List, Optional, Callable
from functools import wraps
from pydantic import BaseModel


def depends_on(*dependencies: str, **dependency_config):
    """
    Decorator to mark a Pydantic model as dependent on other models.
    
    Args:
        *dependencies: Names of models this model depends on
        **dependency_config: Configuration for dependencies
    
    Usage:
        @depends_on('user', 'product')
        class Order(BaseModel):
            user_id: int
            product_id: int
            quantity: int
    """
    def decorator(model_class: Type[BaseModel]):
        # Store dependency info in model
        model_class.__weaver_dependencies__ = {}
        
        for dep in dependencies:
            model_class.__weaver_dependencies__[dep] = dependency_config.get(dep, {})
        
        return model_class
    
    return decorator


def correlate(field_name: str, source_model: str, source_field: Optional[str] = None):
    """
    Decorator to correlate a field with data from another model.
    
    Args:
        field_name: Field name in this model
        source_model: Name of the source model
        source_field: Field name in source model (defaults to same as field_name)
    
    Usage:
        @correlate('user_id', 'user', 'id')
        class Order(BaseModel):
            user_id: int
            quantity: int
    """
    def decorator(model_class: Type[BaseModel]):
        if not hasattr(model_class, '__weaver_correlations__'):
            model_class.__weaver_correlations__ = {}
        
        model_class.__weaver_correlations__[field_name] = {
            'source_model': source_model,
            'source_field': source_field or field_name
        }
        
        return model_class
    
    return decorator


class WeaverBuilder:
    """Fluent API builder for complex data generation scenarios."""
    
    def __init__(self, weaver):
        self.weaver = weaver
        self._models = {}
        self._prompts = {}
        self._count = 1
        self._context = {}
    
    def add_model(self, name: str, model_class: Type[BaseModel], prompt: str = ""):
        """Add a model to the generation chain."""
        self._models[name] = model_class
        self._prompts[name] = prompt or f"Generate realistic {name} data"
        return self
    
    def with_count(self, count: int):
        """Set the number of instances to generate."""
        self._count = count
        return self
    
    def with_context(self, **context):
        """Add context data for generation."""
        self._context.update(context)
        return self
    
    def generate(self):
        """Execute the generation chain."""
        return self.weaver.generate_related(
            models=self._models,
            prompts=self._prompts,
            count=self._count
        )


def batch_generate(count: int):
    """
    Decorator for methods that should generate multiple instances.
    
    Usage:
        @batch_generate(5)
        def generate_users(weaver, prompt):
            return weaver.generate(User, prompt)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract weaver and other arguments
            if 'count' not in kwargs:
                kwargs['count'] = count
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ModelRegistry:
    """Registry for managing model relationships and metadata."""
    
    def __init__(self):
        self._models: Dict[str, Type[BaseModel]] = {}
        self._relationships: Dict[str, List[str]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    def register(self, name: str, model: Type[BaseModel], **metadata):
        """Register a model with metadata."""
        self._models[name] = model
        self._metadata[name] = metadata
        
        # Auto-detect relationships from model fields
        relationships = []
        for field_name, field_info in model.model_fields.items():
            field_type = field_info.annotation
            
            # Check for other BaseModel types
            if isinstance(field_type, type) and issubclass(field_type, BaseModel):
                dep_name = field_type.__name__.lower()
                if dep_name in self._models:
                    relationships.append(dep_name)
        
        self._relationships[name] = relationships
        return self
    
    def get_model(self, name: str) -> Type[BaseModel]:
        """Get a registered model."""
        if name not in self._models:
            raise ValueError(f"Model '{name}' not registered")
        return self._models[name]
    
    def get_dependencies(self, name: str) -> List[str]:
        """Get dependencies for a model."""
        return self._relationships.get(name, [])
    
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """Get metadata for a model."""
        return self._metadata.get(name, {})
    
    def list_models(self) -> List[str]:
        """List all registered models."""
        return list(self._models.keys())


# Global registry instance
registry = ModelRegistry()


def quick_generate(weaver, *model_specs, count: int = 1):
    """
    Quick generation utility for multiple models.
    
    Args:
        weaver: Weaver instance
        *model_specs: Tuples of (model_class, prompt) or just model_class
        count: Number of instances to generate
    
    Usage:
        results = quick_generate(
            weaver,
            (User, "Young adult users"),
            (Product, "Tech products"),
            count=5
        )
    """
    
    models = {}
    prompts = {}
    
    for i, spec in enumerate(model_specs):
        if isinstance(spec, tuple):
            model_class, prompt = spec
        else:
            model_class = spec
            prompt = f"Generate realistic {model_class.__name__} data"
        
        name = model_class.__name__.lower()
        models[name] = model_class
        prompts[name] = prompt
    
    return weaver.generate_related(models, prompts, count)


def smart_prompt(base_prompt: str, **enhancements):
    """
    Create an enhanced prompt with common patterns.
    
    Args:
        base_prompt: Base prompt text
        **enhancements: Enhancement parameters
    
    Usage:
        prompt = smart_prompt(
            "Generate user data",
            realistic=True,
            diverse=True,
            region="Brazil",
            age_range=(18, 65)
        )
    """
    
    enhanced_parts = [base_prompt]
    
    if enhancements.get('realistic', False):
        enhanced_parts.append("Ensure all data is realistic and plausible.")
    
    if enhancements.get('diverse', False):
        enhanced_parts.append("Generate diverse and varied instances.")
    
    if 'region' in enhancements:
        enhanced_parts.append(f"Data should be appropriate for {enhancements['region']} region.")
    
    if 'age_range' in enhancements:
        age_min, age_max = enhancements['age_range']
        enhanced_parts.append(f"Ages should be between {age_min} and {age_max}.")
    
    if 'industry' in enhancements:
        enhanced_parts.append(f"Context should be relevant to {enhancements['industry']} industry.")
    
    return "\n".join(enhanced_parts)