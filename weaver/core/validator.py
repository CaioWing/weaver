"""Response validation for LLM-generated data."""

import json
from typing import Dict, Any, Type, List, Union
from pydantic import BaseModel, ValidationError as PydanticValidationError
from ..exceptions import ValidationError


class ResponseValidator:
    """Validates LLM responses against Pydantic models."""
    
    @staticmethod
    def validate_and_parse(
        response: str,
        model: Type[BaseModel],
        allow_partial: bool = False
    ) -> Union[BaseModel, List[BaseModel]]:
        """
        Validate and parse LLM response into Pydantic model(s).
        
        Args:
            response: Raw JSON response from LLM
            model: Target Pydantic model class
            allow_partial: Whether to allow partial validation (for debugging)
            
        Returns:
            Parsed and validated model instance(s)
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # First, try to parse as JSON
            try:
                data = json.loads(response.strip())
            except json.JSONDecodeError as e:
                # Try to extract JSON from response if it's wrapped in text
                cleaned_response = ResponseValidator._extract_json(response)
                if cleaned_response:
                    data = json.loads(cleaned_response)
                else:
                    raise ValidationError(
                        f"Invalid JSON in LLM response: {str(e)}",
                        llm_response=response
                    ) from e
            
            # Handle array responses (multiple instances)
            if isinstance(data, list):
                return ResponseValidator._validate_list(data, model, allow_partial)
            else:
                return ResponseValidator._validate_single(data, model, allow_partial)
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                f"Unexpected error during validation: {str(e)}",
                llm_response=response
            ) from e
    
    @staticmethod
    def _validate_single(
        data: Dict[str, Any],
        model: Type[BaseModel],
        allow_partial: bool = False
    ) -> BaseModel:
        """Validate single model instance."""
        try:
            return model.model_validate(data)
        except PydanticValidationError as e:
            if allow_partial:
                # Try to create instance with available fields only
                try:
                    valid_fields = {k: v for k, v in data.items() 
                                  if k in model.model_fields}
                    return model.model_validate(valid_fields)
                except PydanticValidationError:
                    pass
            
            # Format validation errors for better debugging
            error_details = ResponseValidator._format_validation_errors(e.errors())
            raise ValidationError(
                f"Validation failed for {model.__name__}: {error_details}",
                llm_response=json.dumps(data, indent=2),
                validation_errors=e.errors()
            ) from e
    
    @staticmethod
    def _validate_list(
        data: List[Dict[str, Any]],
        model: Type[BaseModel],
        allow_partial: bool = False
    ) -> List[BaseModel]:
        """Validate list of model instances."""
        results = []
        errors = []
        
        for i, item in enumerate(data):
            try:
                validated = ResponseValidator._validate_single(item, model, allow_partial)
                results.append(validated)
            except ValidationError as e:
                errors.append(f"Item {i}: {e}")
        
        if errors and not allow_partial:
            raise ValidationError(
                f"Validation failed for multiple items: {'; '.join(errors)}",
                llm_response=json.dumps(data, indent=2)
            )
        
        return results
    
    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Extract JSON from text that might contain additional content.
        
        Args:
            text: Text that might contain JSON
            
        Returns:
            Extracted JSON string or empty string if not found
        """
        # Remove common markdown code block markers
        text = text.strip()
        
        # Handle markdown code blocks
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end != -1:
                text = text[start:end].strip()
        elif '```' in text:
            # Generic code block
            start = text.find('```') + 3
            end = text.find('```', start)
            if end != -1:
                text = text[start:end].strip()
        
        # Remove leading/trailing whitespace and newlines
        text = text.strip()
        
        # Look for JSON object/array boundaries, prioritizing arrays
        # Try arrays first (since they can contain objects)
        start_chars = ['[', '{']
        end_chars = [']', '}']
        
        for start_char, end_char in zip(start_chars, end_chars):
            start_idx = text.find(start_char)
            if start_idx == -1:
                continue
            
            # Find the matching closing bracket/brace
            count = 0
            in_string = False
            escape_next = False
            
            for i, char in enumerate(text[start_idx:], start_idx):
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char == start_char:
                        count += 1
                    elif char == end_char:
                        count -= 1
                        if count == 0:
                            return text[start_idx:i+1]
        
        return ""
    
    @staticmethod
    def _format_validation_errors(errors: List[Dict[str, Any]]) -> str:
        """
        Format Pydantic validation errors for better readability.
        
        Args:
            errors: List of Pydantic error dictionaries
            
        Returns:
            Formatted error string
        """
        formatted_errors = []
        
        for error in errors:
            location = " -> ".join(str(loc) for loc in error.get("loc", []))
            message = error.get("msg", "Unknown error")
            error_type = error.get("type", "unknown")
            
            if location:
                formatted_errors.append(f"{location}: {message} (type: {error_type})")
            else:
                formatted_errors.append(f"{message} (type: {error_type})")
        
        return "; ".join(formatted_errors)
    
    @staticmethod
    def create_validation_diff(
        expected_schema: Dict[str, Any],
        actual_data: Dict[str, Any]
    ) -> str:
        """
        Create a diff between expected schema and actual data for debugging.
        
        Args:
            expected_schema: JSON schema that was expected
            actual_data: Actual data that failed validation
            
        Returns:
            Human-readable diff string
        """
        diff_lines = []
        
        # Check for missing required fields
        required_fields = expected_schema.get("required", [])
        properties = expected_schema.get("properties", {})
        
        for field in required_fields:
            if field not in actual_data:
                field_type = properties.get(field, {}).get("type", "unknown")
                diff_lines.append(f"- Missing required field '{field}' (type: {field_type})")
        
        # Check for unexpected fields
        for field in actual_data:
            if field not in properties:
                diff_lines.append(f"+ Unexpected field '{field}' with value: {actual_data[field]}")
        
        # Check for type mismatches
        for field, value in actual_data.items():
            if field in properties:
                expected_type = properties[field].get("type")
                actual_type = type(value).__name__.lower()
                
                type_mapping = {
                    "str": "string",
                    "int": "integer", 
                    "float": "number",
                    "bool": "boolean",
                    "list": "array",
                    "dict": "object"
                }
                
                actual_json_type = type_mapping.get(actual_type, actual_type)
                
                if expected_type and expected_type != actual_json_type:
                    diff_lines.append(
                        f"! Type mismatch for '{field}': expected {expected_type}, "
                        f"got {actual_json_type} ({value})"
                    )
        
        return "\n".join(diff_lines) if diff_lines else "No obvious schema mismatches found"