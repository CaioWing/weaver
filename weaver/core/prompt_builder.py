"""Intelligent prompt building module for enhanced data generation."""

from typing import Type, Dict, Any, Union
from pydantic import BaseModel


class PromptBuilder:
    """Handles intelligent prompt construction and enhancement."""
    
    @staticmethod
    def infer_prompt(model_class: Type[BaseModel], options: Dict[str, Any] = None) -> str:
        """Intelligently infer a prompt based on model name and options."""
        
        if options is None:
            options = {}
            
        model_name = model_class.__name__
        base_prompt = f"Generate realistic {model_name.lower()} data"
        
        # Add contextual hints based on model name patterns
        if 'user' in model_name.lower():
            base_prompt = "Generate diverse user profiles with realistic personal information"
        elif 'product' in model_name.lower():
            base_prompt = "Generate varied product listings with realistic prices and descriptions"
        elif 'order' in model_name.lower():
            base_prompt = "Generate realistic order data with proper quantities and totals"
        elif 'company' in model_name.lower():
            base_prompt = "Generate realistic company information with proper business details"
        elif 'address' in model_name.lower():
            base_prompt = "Generate realistic address information with proper formatting"
        elif 'payment' in model_name.lower():
            base_prompt = "Generate realistic payment information with valid formats"
        elif 'customer' in model_name.lower():
            base_prompt = "Generate diverse customer profiles with realistic demographics"
        elif 'employee' in model_name.lower():
            base_prompt = "Generate realistic employee information with job details"
        
        return PromptBuilder.enhance_prompt(base_prompt, model_class, options)
    
    @staticmethod
    def enhance_prompt(
        base_prompt: str, 
        model_class: Type[BaseModel], 
        options: Dict[str, Any] = None
    ) -> str:
        """Enhance a prompt based on options (similar to smart_prompt functionality)."""
        
        if options is None:
            options = {}
        
        if not base_prompt:
            base_prompt = f"Generate realistic {model_class.__name__.lower()} data"
        
        enhancements = []
        
        # Core quality enhancements
        if options.get('realistic', True):
            enhancements.append("Ensure all data is realistic and plausible.")
        
        if options.get('diverse', True):
            enhancements.append("Generate diverse and varied instances.")
        
        # Geographic and cultural enhancements
        if 'region' in options:
            enhancements.append(f"Data should be appropriate for {options['region']} region.")
        
        if 'country' in options:
            enhancements.append(f"Use {options['country']} country-specific conventions.")
        
        if 'language' in options:
            enhancements.append(f"Use {options['language']} language and cultural context.")
        
        # Demographic enhancements
        if 'age_range' in options:
            age_min, age_max = options['age_range']
            enhancements.append(f"Ages should be between {age_min} and {age_max}.")
        
        if 'gender' in options:
            enhancements.append(f"Focus on {options['gender']} demographics.")
        
        # Business and industry enhancements
        if 'industry' in options:
            enhancements.append(f"Context should be relevant to {options['industry']} industry.")
        
        if 'business_size' in options:
            enhancements.append(f"Target {options['business_size']} business context.")
        
        # Temporal enhancements
        if 'time_period' in options:
            enhancements.append(f"Data should reflect {options['time_period']} time period.")
        
        if 'season' in options:
            enhancements.append(f"Consider {options['season']} seasonal context.")
        
        # Quality and style enhancements
        if 'premium' in options and options['premium']:
            enhancements.append("Focus on premium, high-quality options.")
        
        if 'budget' in options and options['budget']:
            enhancements.append("Focus on budget-friendly, economical options.")
        
        if 'professional' in options and options['professional']:
            enhancements.append("Use professional, business-appropriate context.")
        
        # Combine base prompt with enhancements
        if enhancements:
            return f"{base_prompt}\n\n" + "\n".join(enhancements)
        
        return base_prompt
    
    @staticmethod
    def build_correlation_prompt(
        model_class: Type[BaseModel],
        base_prompt: str,
        correlation_context: str
    ) -> str:
        """Build a prompt with correlation requirements for dependent models."""
        
        if not correlation_context:
            return base_prompt
        
        enhanced_prompt = f"""{base_prompt}

CRITICAL CORRELATION REQUIREMENTS:
{correlation_context}

The generated data MUST reference the exact IDs and values provided above. Do not create new IDs - only use the ones listed."""
        
        return enhanced_prompt
    
    @staticmethod
    def build_system_prompt(
        model_class: Type[BaseModel],
        has_correlations: bool = False
    ) -> str:
        """Build system prompt based on model and correlation requirements."""
        
        base_system = f"""Generate realistic, varied {model_class.__name__} data.

CORE RULES:
- Always return valid data matching the exact schema
- Use diverse, realistic values 
- Ensure all required fields are present
- Be creative but maintain data consistency"""

        if has_correlations:
            correlation_rules = """

CORRELATION RULES:
- MUST use only the exact IDs provided in the context
- MUST maintain referential integrity 
- All foreign key relationships must be valid
- Generate diverse but correlated data
- Do NOT create new IDs - only reference existing ones"""
            
            return base_system + correlation_rules
        
        return base_system
    
    @staticmethod
    def build_independent_system_prompt(model_class: Type[BaseModel]) -> str:
        """Build system prompt for independent models without dependencies."""
        
        return f"""Generate realistic, varied {model_class.__name__} data.
        
RULES:
- Always return valid data matching the exact schema
- Use diverse, realistic values 
- Ensure all required fields are present  
- Generate unique IDs starting from 1
- Be creative but maintain data consistency"""
    
    @staticmethod
    def normalize_prompts_input(
        prompts: Union[str, Dict[str, str]],
        model_names: list,
        options: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """Normalize different prompt input formats to a consistent dict format."""
        
        if options is None:
            options = {}
        
        if isinstance(prompts, str):
            # Single prompt for all models
            return {name: prompts for name in model_names}
        elif isinstance(prompts, dict):
            # Dict of prompts - fill missing ones
            result = {}
            for name in model_names:
                if name in prompts:
                    result[name] = prompts[name]
                else:
                    # Generate default prompt for missing models
                    result[name] = f"Generate realistic {name} data"
            return result
        elif prompts is None or prompts == "":
            # No prompts provided - generate defaults
            return {name: f"Generate realistic {name} data" for name in model_names}
        else:
            raise ValueError(f"Invalid prompts type: {type(prompts)}. Expected str or dict.")