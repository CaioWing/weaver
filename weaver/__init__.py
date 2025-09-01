"""Weaver: Generate realistic test data using LLMs and Pydantic models."""

from .core import Weaver
from .exceptions import (
    WeaverError,
    ValidationError,
    LLMProviderError,
    SchemaConversionError,
    CacheError,
    TemplateError,
    DatabaseIntrospectionError,
    ExportError,
)

__version__ = "0.1.0"
__author__ = "Weaver Team"
__email__ = "team@weaver.dev"

__all__ = [
    "Weaver",
    "WeaverError",
    "ValidationError", 
    "LLMProviderError",
    "SchemaConversionError",
    "CacheError",
    "TemplateError",
    "DatabaseIntrospectionError",
    "ExportError",
]