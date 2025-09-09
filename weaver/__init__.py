"""Weaver: Generate realistic test data using Pydantic AI."""

from .core import Weaver
from .exceptions import WeaverError, ValidationError

__version__ = "0.1.0"
__author__ = "CaioWing"
__email__ = "caio@airis-tech.com"

__all__ = [
    "Weaver",
    "WeaverError", 
    "ValidationError",
]