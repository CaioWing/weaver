# Weaver Project Architecture

## Overview

Weaver is a Python library that generates realistic test data using LLMs and Pydantic models. The architecture is designed to be modular, extensible, and follows Python best practices.

## Project Structure

```
weaver/
├── pyproject.toml                  # Modern Python packaging
├── README.md
├── weaver/
│   ├── __init__.py                # Public API exports
│   ├── core/
│   │   ├── __init__.py
│   │   ├── weaver.py              # Main Weaver class
│   │   ├── schema_converter.py    # Pydantic → JSON Schema
│   │   └── validator.py           # Response validation
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract LLM provider
│   │   ├── openai_provider.py     # OpenAI implementation
│   │   └── registry.py            # Provider registration
│   ├── cache/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract cache interface
│   │   └── file_cache.py          # File-based cache
│   ├── database/
│   │   ├── __init__.py
│   │   ├── introspector.py        # DB schema introspection
│   │   └── connectors/            # DB-specific connectors
│   ├── templates/
│   │   ├── __init__.py
│   │   └── manager.py             # Template system
│   ├── exports/
│   │   ├── __init__.py
│   │   ├── base.py                # Abstract exporter
│   │   ├── sql_exporter.py        # SQL INSERT generation
│   │   └── csv_exporter.py        # CSV generation
│   └── exceptions.py              # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_providers/
│   └── fixtures/
└── examples/
    ├── basic_usage.py
    └── database_introspection.py
```

## Key Architectural Principles

### 1. Modular Design
- **Core Module**: Contains the main Weaver class and fundamental operations
- **Providers Module**: Pluggable LLM integrations (OpenAI, Claude, local models)
- **Extensions**: Cache, database, templates, and export functionality in separate modules

### 2. Abstract Interfaces
All major components use abstract base classes to ensure consistency and enable easy extension:

- `LLMProvider`: Abstract base for all LLM integrations
- `CacheInterface`: Pluggable caching system
- `DatabaseIntrospector`: DB schema reading interface
- `Exporter`: Different output format generators

### 3. Dependency Injection
The main Weaver class accepts provider instances, making it easy to:
- Switch between different LLM providers
- Mock providers for testing
- Add custom implementations

## Core Components

### Weaver Core (`weaver/core/`)

**weaver.py**: Main orchestrator class
- Coordinates between schema conversion, LLM calls, and validation
- Handles caching and template resolution
- Public API entry point

**schema_converter.py**: Pydantic to JSON Schema conversion
- Converts Pydantic models to JSON Schema format
- Handles nested models, lists, enums, and advanced types
- Optimizes schema for LLM consumption

**validator.py**: Response validation
- Validates LLM responses against original Pydantic models
- Provides detailed error messages for validation failures
- Handles retry logic for invalid responses

### LLM Providers (`weaver/providers/`)

**base.py**: Abstract provider interface
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, schema: dict) -> str:
        pass
```

**openai_provider.py**: OpenAI GPT implementation
- Uses OpenAI's JSON mode for structured output
- Handles rate limiting and error recovery
- Configurable model selection

**registry.py**: Provider management
- Dynamic provider registration
- Provider discovery and instantiation
- Configuration management

### Caching System (`weaver/cache/`)

**base.py**: Abstract cache interface
- Defines caching contract
- Supports both sync and async operations

**file_cache.py**: File-based implementation
- Stores cache as JSON files
- Configurable cache directory and TTL
- Automatic cleanup of expired entries

## Extension Points

### Adding New LLM Providers
1. Inherit from `LLMProvider`
2. Implement `generate()` method
3. Register with provider registry
4. Add configuration options

### Adding New Export Formats
1. Inherit from `Exporter`
2. Implement format-specific generation
3. Register with export system

### Database Connectors
1. Implement database-specific introspection
2. Follow common interface for schema extraction
3. Handle database-specific data types

## Development Roadmap Alignment

### Month 1: MVP Core
- ✅ Core Weaver class with generate functionality
- ✅ Pydantic schema conversion
- ✅ OpenAI provider integration
- ✅ Basic validation system
- ✅ Support for nested models and lists

### Month 2: Developer Experience
- 🔄 File-based caching system
- 🔄 Advanced Pydantic type support (Enum, Union, Literal)
- 🔄 Enhanced error handling and reporting
- 🔄 PyPI packaging and distribution

### Month 3: Enterprise Features
- 🔄 Database schema introspection
- 🔄 Template system
- 🔄 Multiple export formats (SQL, CSV)
- 🔄 Advanced configuration options

## Testing Strategy

- **Unit Tests**: Each module tested independently
- **Integration Tests**: End-to-end workflow testing
- **Provider Tests**: Mock LLM responses for consistent testing
- **Fixtures**: Reusable test data and models

## Configuration

The library supports multiple configuration methods:
- Environment variables
- Configuration files (YAML/JSON)
- Direct instantiation parameters
- Runtime configuration updates

This architecture ensures Weaver is extensible, maintainable, and ready for both open-source adoption and future commercial features.