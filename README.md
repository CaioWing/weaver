# Weaver

**Generate realistic test data using LLMs and Pydantic models**

Weaver is a Python library that makes it incredibly easy to generate realistic, contextual test data for your applications. Simply describe what you want in natural language, provide a Pydantic model, and let AI do the rest.

## Features

- **AI-Powered**: Uses OpenAI GPT models for intelligent data generation
- **Type-Safe**: Built on Pydantic for robust data validation
- **Context-Aware**: Generates data that makes sense for your specific use case
- **Extensible**: Modular architecture supports multiple LLM providers
- **Easy to Use**: Simple, intuitive API that gets you started in minutes

## Quick Start

### Installation

```bash
pip install data-weaver
```

### Basic Usage

```python
from pydantic import BaseModel
from typing import List
from weaver import Weaver

# Define your data models
class Order(BaseModel):
    product_id: int
    quantity: int
    price: float

class User(BaseModel):
    name: str
    email: str
    age: int
    orders: List[Order]

# Initialize Weaver
weaver = Weaver()

# Generate realistic test data
user = weaver.generate(
    model=User,
    prompt="A 25-year-old user named João who made 2 orders of different products"
)

print(user.model_dump_json(indent=2))
```

**Output:**
```json
{
  "name": "João da Silva",
  "email": "joao.silva@example.com",
  "age": 25,
  "orders": [
    { "product_id": 101, "quantity": 2, "price": 29.99 },
    { "product_id": 204, "quantity": 1, "price": 89.50 }
  ]
}
```

## Configuration

### Environment Variables

Set your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Custom Configuration

```python
# OpenAI (direct)
weaver = Weaver(
    provider="openai",
    model="gpt-4-turbo",
    temperature=0.2
)

# OpenRouter (access multiple models)
weaver = Weaver(
    provider="openrouter",
    model="anthropic/claude-3.5-sonnet",  # or any OpenRouter model
    temperature=0.1
)
```

### Multiple LLM Providers

Weaver supports multiple LLM providers through a unified interface:

**OpenAI Direct:**
- Native OpenAI API access
- JSON mode support
- Fast and reliable

**OpenRouter:**
- Access to 100+ models (GPT, Claude, Gemini, Llama, etc.)
- Single API key for all providers
- Competitive pricing
- Easy model switching

## Architecture

Weaver is built with a modular architecture that makes it easy to:

- **Add new LLM providers** (OpenAI, Claude, local models)
- **Extend functionality** (caching, templates, database integration)
- **Customize behavior** (validation, error handling, retry logic)

## Roadmap

### Month 1: MVP
- [x] Core generation functionality
- [x] OpenAI provider integration
- [x] Pydantic model support
- [x] Basic validation and error handling

### Month 2: Developer Experience
- [ ] PyPI package distribution
- [ ] Caching system
- [ ] Enhanced error reporting
- [ ] Support for Enums, Unions, and advanced types

## License

MIT License - see LICENSE file for details.

---