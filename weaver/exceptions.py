"""Custom exceptions for Weaver library."""


class WeaverError(Exception):
    """Base exception for all Weaver errors."""
    pass


class SchemaConversionError(WeaverError):
    """Raised when Pydantic model cannot be converted to JSON Schema."""
    pass


class LLMProviderError(WeaverError):
    """Raised when LLM provider encounters an error."""
    pass


class ValidationError(WeaverError):
    """Raised when LLM response fails validation against Pydantic model."""
    
    def __init__(self, message: str, llm_response: str = None, validation_errors: list = None):
        super().__init__(message)
        self.llm_response = llm_response
        self.validation_errors = validation_errors or []


class CacheError(WeaverError):
    """Raised when cache operations fail."""
    pass


class TemplateError(WeaverError):
    """Raised when template operations fail."""
    pass


class DatabaseIntrospectionError(WeaverError):
    """Raised when database introspection fails."""
    pass


class ExportError(WeaverError):
    """Raised when export operations fail."""
    pass