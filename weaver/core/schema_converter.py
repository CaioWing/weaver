"""Convert Pydantic models to JSON Schema for LLM consumption."""

import json
from typing import Dict, Any, Type, get_origin, get_args
from datetime import datetime, date, time
from enum import Enum
from pydantic import BaseModel
from pydantic._internal._generate_schema import GenerateSchema
from pydantic._internal._config import ConfigWrapper
from ..exceptions import SchemaConversionError


class SchemaConverter:
    """Converts Pydantic models to JSON Schema optimized for LLM consumption."""
    
    @staticmethod
    def convert_to_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
        """
        Convert a Pydantic model to JSON Schema.
        
        Args:
            model: Pydantic model class
            
        Returns:
            JSON Schema dictionary
            
        Raises:
            SchemaConversionError: If conversion fails
        """
        try:
            # Get the JSON schema from Pydantic
            schema = model.model_json_schema()
            
            # Clean up the schema for LLM consumption
            cleaned_schema = SchemaConverter._clean_schema(schema)
            
            return cleaned_schema
            
        except Exception as e:
            raise SchemaConversionError(
                f"Failed to convert {model.__name__} to JSON Schema: {str(e)}"
            ) from e
    
    @staticmethod
    def _clean_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean up the schema for better LLM understanding.
        
        Args:
            schema: Raw JSON Schema from Pydantic
            
        Returns:
            Cleaned JSON Schema
        """
        # Remove Pydantic-specific fields that might confuse LLMs
        fields_to_remove = [
            "title",
            "$defs"  # We'll inline definitions instead
        ]
        
        cleaned = {k: v for k, v in schema.items() if k not in fields_to_remove}
        
        # Inline definitions to avoid references
        if "$defs" in schema:
            cleaned = SchemaConverter._inline_definitions(cleaned, schema["$defs"])
        
        # Add helpful descriptions for better LLM understanding
        cleaned = SchemaConverter._enhance_descriptions(cleaned)
        
        return cleaned
    
    @staticmethod
    def _inline_definitions(schema: Dict[str, Any], definitions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inline $ref definitions to avoid complex references.
        
        Args:
            schema: Schema to process
            definitions: Definitions to inline
            
        Returns:
            Schema with inlined definitions
        """
        def replace_refs(obj: Any) -> Any:
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref_path = obj["$ref"]
                    if ref_path.startswith("#/$defs/"):
                        def_name = ref_path.split("/")[-1]
                        if def_name in definitions:
                            # Recursively replace refs in the definition
                            return replace_refs(definitions[def_name])
                    return obj
                else:
                    return {k: replace_refs(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [replace_refs(item) for item in obj]
            else:
                return obj
        
        return replace_refs(schema)
    
    @staticmethod
    def _enhance_descriptions(schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add helpful descriptions for LLM understanding.
        
        Args:
            schema: Schema to enhance
            
        Returns:
            Enhanced schema
        """
        def enhance_property(prop: Dict[str, Any], field_name: str) -> Dict[str, Any]:
            prop_type = prop.get("type", "unknown")
            prop_format = prop.get("format", "")
            
            # Add format hints for common types
            if prop_type == "string":
                if field_name.lower() in ["email", "e_mail", "email_address"]:
                    prop["format"] = "email"
                    if "description" not in prop:
                        prop["description"] = "A valid email address"
                elif field_name.lower() in ["name", "first_name", "last_name", "full_name"]:
                    if "description" not in prop:
                        prop["description"] = "A realistic human name"
                elif field_name.lower() in ["phone", "telephone", "phone_number"]:
                    if "description" not in prop:
                        prop["description"] = "A valid phone number"
                elif prop_format == "date":
                    # This is a date field (not datetime)
                    if "description" not in prop:
                        prop["description"] = "Date in YYYY-MM-DD format (date only, no time)"
                elif "date" in field_name.lower() and prop_format != "date":
                    # This might be a datetime field
                    prop["format"] = "date-time"
                    if "description" not in prop:
                        prop["description"] = "ISO 8601 datetime string"
                elif field_name.lower() == "cpf":
                    if "description" not in prop:
                        prop["description"] = "Brazilian CPF in format XXX.XXX.XXX-XX (exactly 11 digits [0-9] with dots and dash)"
                elif field_name.lower() in ["zip_code", "postal_code", "cep"]:
                    if "description" not in prop:
                        prop["description"] = "Brazilian ZIP code in format XXXXX-XXX (8 digits [0-9] with optional dash)"
            
            elif prop_type == "integer":
                if field_name.lower() in ["id", "user_id", "product_id"]:
                    if "description" not in prop:
                        prop["description"] = "A positive integer ID"
                elif field_name.lower() in ["age"]:
                    if "description" not in prop:
                        prop["description"] = "Age in years (positive integer)"
                elif field_name.lower() in ["quantity", "count", "amount"]:
                    if "description" not in prop:
                        prop["description"] = "A positive integer quantity"
            
            # Recursively enhance nested objects
            if prop_type == "object" and "properties" in prop:
                for nested_name, nested_prop in prop["properties"].items():
                    prop["properties"][nested_name] = enhance_property(nested_prop, nested_name)
            
            elif prop_type == "array" and "items" in prop:
                if isinstance(prop["items"], dict):
                    prop["items"] = enhance_property(prop["items"], f"{field_name}_item")
            
            return prop
        
        # Enhance root properties
        if "properties" in schema:
            for field_name, field_schema in schema["properties"].items():
                schema["properties"][field_name] = enhance_property(field_schema, field_name)
        
        return schema
    
    @staticmethod
    def create_system_prompt(schema: Dict[str, Any], model_name: str = None) -> str:
        """
        Create a system prompt that includes the schema for the LLM.
        
        Args:
            schema: JSON Schema dictionary
            model_name: Name of the Pydantic model (optional)
            
        Returns:
            System prompt string
        """
        model_description = f" for the {model_name} model" if model_name else ""
        
        prompt = f"""You are a data generation assistant. Generate realistic test data{model_description} based on the user's natural language description.

IMPORTANT INSTRUCTIONS:
1. Generate ONLY valid JSON that strictly conforms to the provided schema
2. Use realistic, contextual data that makes sense for the described scenario
3. Ensure all required fields are included
4. Use appropriate data types and formats
5. Generate diverse, non-repetitive data
6. Do not include any explanations, comments, or text outside the JSON

JSON Schema:
{json.dumps(schema, indent=2)}

Generate valid JSON that matches this schema exactly."""
        
        return prompt