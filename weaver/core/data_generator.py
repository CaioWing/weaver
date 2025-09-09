"""Data generation module handling LLM interactions and batch processing."""

import asyncio
from typing import Type, List, Dict, Any, Union
from pydantic import BaseModel, create_model as pydantic_create_model
from pydantic_ai import Agent

from .dependency_resolver import DependencyResolver
from .prompt_builder import PromptBuilder
from ..exceptions import WeaverError


class DataGenerator:
    """Handles the actual data generation using LLM agents."""
    
    def __init__(self, model, model_name: str, provider_name: str):
        """Initialize the data generator with model configuration."""
        self.model = model
        self.model_name = model_name
        self.provider_name = provider_name
    
    def generate_independent(
        self, 
        model_class: Type[BaseModel], 
        prompt: str, 
        count: int
    ) -> Union[BaseModel, List[BaseModel]]:
        """Generate data for models without dependencies."""
        
        system_prompt = PromptBuilder.build_independent_system_prompt(model_class)
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            retries=3,
        )
        
        if count == 1:
            result = self._run_agent(agent, prompt, model_class)
            return result.output
        else:
            return self._generate_batch(agent, model_class, prompt, count)
    
    def generate_with_correlations(
        self, 
        model_class: Type[BaseModel], 
        prompt: str, 
        count: int,
        generated_pool: Dict[str, Any],
        dependencies: List[str]
    ) -> Union[BaseModel, List[BaseModel]]:
        """Generate data that correlates with previously generated data."""
        
        # Build context with available dependency data
        correlation_context = DependencyResolver.build_correlation_context(
            model_class, generated_pool, dependencies
        )
        
        enhanced_prompt = PromptBuilder.build_correlation_prompt(
            model_class, prompt, correlation_context
        )
        
        system_prompt = PromptBuilder.build_system_prompt(
            model_class, has_correlations=True
        )
        
        agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            retries=3,
        )
        
        if count == 1:
            result = self._run_agent(agent, enhanced_prompt, model_class)
            return result.output
        else:
            return self._generate_batch(agent, model_class, enhanced_prompt, count)
    
    def generate_related_data(
        self,
        models: Dict[str, Type[BaseModel]],
        prompts: Dict[str, str],
        count: int = 1
    ) -> Dict[str, Union[BaseModel, List[BaseModel]]]:
        """Generate related data for multiple models with real correlations."""
        
        try:
            # Sort models by dependency order (topological sort)
            ordered_models = DependencyResolver.topological_sort(models)
            
            results = {}
            generated_pool = {}  # Pool of all generated instances by model type
            
            for model_name in ordered_models:
                model_class = models[model_name]
                prompt = prompts.get(model_name, f"Generate realistic {model_name} data")
                
                # Check if this model has dependencies
                dependencies = DependencyResolver.extract_dependency_names(model_class)
                available_deps = [dep for dep in dependencies if dep in generated_pool]
                
                if not available_deps:
                    # No dependencies - generate independently
                    generated = self.generate_independent(model_class, prompt, count)
                else:
                    # Has dependencies - generate with valid correlations  
                    generated = self.generate_with_correlations(
                        model_class, prompt, count, generated_pool, available_deps
                    )
                
                results[model_name] = generated
                generated_pool[model_name] = generated
                
            return results
            
        except Exception as e:
            raise WeaverError(f"Related generation failed: {str(e)}") from e
    
    def _generate_batch(
        self, 
        agent: Agent, 
        model: Type[BaseModel], 
        prompt: str, 
        count: int
    ) -> List[BaseModel]:
        """Optimized batch generation using a single LLM call."""
        
        # Create a dynamic batch model
        batch_model_name = f"Batch{model.__name__}"
        
        # Create batch model with items field
        BatchModel = pydantic_create_model(
            batch_model_name,
            items=(List[model], ...)
        )
        
        batch_prompt = f"""Generate exactly {count} different, varied instances of {model.__name__}.
        
Original prompt: {prompt}
        
Ensure each instance is unique and realistic. Return all {count} instances in the 'items' array."""
        
        result = self._run_agent(agent, batch_prompt, BatchModel)
        return result.output.items[:count]
    
    def _run_agent(self, agent: Agent, prompt: str, output_type: Type[BaseModel]):
        """Run agent with proper async/sync handling."""
        
        import signal
        import concurrent.futures
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Agent execution timed out")
        
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                
                # Always use thread approach in Jupyter to avoid nest_asyncio issues
                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        
                        result = new_loop.run_until_complete(
                            agent.run(prompt, output_type=output_type)
                        )
                        return result
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    try:
                        result = future.result(timeout=60)  # 60 second timeout
                        return result
                    except concurrent.futures.TimeoutError:
                        future.cancel()
                        raise WeaverError("LLM request timed out after 60 seconds")
                    
            except RuntimeError:
                # No event loop running, safe to use run_sync
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(60)  # 60 second timeout
                
                try:
                    result = agent.run_sync(prompt, output_type=output_type)
                    return result
                finally:
                    signal.alarm(0)  # Clear timeout
                
        except TimeoutError:
            raise WeaverError("LLM request timed out")
        except Exception as e:
            raise WeaverError(f"Agent execution failed: {str(e)}") from e


class BatchProcessor:
    """Handles batch processing and optimization for multiple model generation."""
    
    @staticmethod
    def optimize_generation_order(
        models: Dict[str, Type[BaseModel]]
    ) -> List[str]:
        """Optimize the order of model generation for maximum efficiency."""
        
        # For now, use topological sort
        # Could be enhanced with cost-based optimization in the future
        return DependencyResolver.topological_sort(models)
    
    @staticmethod
    def estimate_generation_cost(
        models: Dict[str, Type[BaseModel]], 
        count: int
    ) -> Dict[str, int]:
        """Estimate the generation cost for each model (for future optimization)."""
        
        costs = {}
        
        for name, model_class in models.items():
            # Basic cost estimation based on field count and complexity
            field_count = len(model_class.model_fields)
            dependencies = DependencyResolver.extract_dependency_names(model_class)
            
            # Base cost + dependency cost + field complexity cost
            base_cost = count
            dependency_cost = len(dependencies) * count * 0.5
            field_cost = field_count * count * 0.1
            
            costs[name] = int(base_cost + dependency_cost + field_cost)
        
        return costs