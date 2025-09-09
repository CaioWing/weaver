"""Dependency resolution module for automatic model relationship detection."""

from typing import Type, List, Dict, Union
from pydantic import BaseModel


class DependencyResolver:
    """Handles automatic detection and resolution of model dependencies."""
    
    @staticmethod
    def auto_detect_dependencies(model_class: Type[BaseModel]) -> List[Type[BaseModel]]:
        """Automatically detect dependency models from field types."""
        
        dependencies = []
        
        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation
            
            # Handle List[Model] types
            if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                inner_type = field_type.__args__[0]
                if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                    dependencies.append(inner_type)
            
            # Handle direct Model types
            elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                dependencies.append(field_type)
            
            # Handle Optional[Model] types (Union with None)
            elif hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                for union_type in field_type.__args__:
                    if (isinstance(union_type, type) and 
                        issubclass(union_type, BaseModel) and 
                        union_type != type(None)):
                        dependencies.append(union_type)
        
        return dependencies
    
    @staticmethod
    def extract_dependency_names(model_class: Type[BaseModel]) -> List[str]:
        """Extract dependency names from a model class using pure auto-detection."""
        
        dependencies = []
        
        # Auto-detect from field types only (no decorators needed)
        for field_name, field_info in model_class.model_fields.items():
            field_type = field_info.annotation
            
            # Handle List[Model] types
            if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                inner_type = field_type.__args__[0]
                if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                    dependencies.append(inner_type.__name__.lower())
            
            # Handle direct Model types
            elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
                dependencies.append(field_type.__name__.lower())
            
            # Handle Optional[Model] types
            elif hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                for union_type in field_type.__args__:
                    if (isinstance(union_type, type) and 
                        issubclass(union_type, BaseModel) and 
                        union_type != type(None)):
                        dependencies.append(union_type.__name__.lower())
        
        return list(set(dependencies))  # Remove duplicates
    
    @staticmethod
    def topological_sort(models: Dict[str, Type[BaseModel]]) -> List[str]:
        """Sort models by dependency order using topological sort (Kahn's algorithm)."""
        
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        # Initialize graph and in-degree count
        for name in models.keys():
            graph[name] = []
            in_degree[name] = 0
        
        # Build edges based on dependencies
        for name, model_class in models.items():
            dependencies = DependencyResolver.extract_dependency_names(model_class)
            
            for dep in dependencies:
                if dep in models:
                    graph[dep].append(name)  # dep -> name
                    in_degree[name] += 1
        
        # Kahn's algorithm for topological sorting
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(models):
            # Fallback to original order if cycle detected
            return list(models.keys())
        
        return result
    
    @staticmethod
    def build_correlation_context(
        model_class: Type[BaseModel], 
        generated_pool: Dict[str, any],
        dependencies: List[str]
    ) -> str:
        """Build detailed correlation context for dependent models."""
        
        context_parts = []
        
        for dep_name in dependencies:
            if dep_name not in generated_pool:
                continue
                
            dep_data = generated_pool[dep_name]
            dep_instances = dep_data if isinstance(dep_data, list) else [dep_data]
            
            # Extract key identifying fields (typically 'id', 'name', etc.)
            id_info = []
            for instance in dep_instances:
                instance_info = {}
                
                # Try to find ID field first
                if hasattr(instance, 'id'):
                    instance_info['id'] = instance.id
                elif hasattr(instance, 'name'):
                    instance_info['name'] = instance.name
                
                # Include other key fields for context (avoid long strings)
                for field_name, field_value in instance.model_dump().items():
                    if field_name not in instance_info and len(str(field_value)) < 50:
                        instance_info[field_name] = field_value
                        
                id_info.append(instance_info)
            
            context_parts.append(f"""
Available {dep_name} instances to reference:
{chr(10).join([f"  - {info}" for info in id_info[:10]])}  # Show max 10 instances
""")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def normalize_models_input(
        models: Union[Dict[str, Type[BaseModel]], List[Type[BaseModel]]]
    ) -> Dict[str, Type[BaseModel]]:
        """Normalize different model input formats to a consistent dict format."""
        
        if isinstance(models, list):
            return {model.__name__.lower(): model for model in models}
        elif isinstance(models, dict):
            return models
        else:
            raise ValueError(f"Invalid models type: {type(models)}. Expected dict or list.")