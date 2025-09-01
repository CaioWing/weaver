"""Test the project structure without requiring API keys."""

from pydantic import BaseModel
from typing import List

# Test imports
try:
    from weaver import Weaver, WeaverError, ValidationError
    from weaver.core import SchemaConverter
    from weaver.providers import LLMProvider, registry
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test models
class Order(BaseModel):
    product_id: int
    quantity: int
    price: float

class User(BaseModel):
    name: str
    email: str
    age: int
    orders: List[Order]

def test_schema_conversion():
    """Test schema conversion functionality."""
    print("\n📋 Testing schema conversion...")
    
    try:
        # Test schema conversion
        schema = SchemaConverter.convert_to_json_schema(User)
        print(f"✅ Schema conversion successful")
        
        # Test system prompt creation
        system_prompt = SchemaConverter.create_system_prompt(schema, "User")
        print(f"✅ System prompt creation successful")
        
        # Show a bit of the schema
        properties = schema.get('properties', {})
        print(f"📝 Schema has {len(properties)} properties: {list(properties.keys())}")
        
    except Exception as e:
        print(f"❌ Schema conversion error: {e}")

def test_provider_registry():
    """Test provider registry."""
    print("\n🔧 Testing provider registry...")
    
    try:
        providers = registry.list_providers()
        print(f"✅ Registry working. Available providers: {providers}")
        
        # Test getting provider without config (should fail gracefully)
        try:
            provider = registry.get_provider("openai", api_key="test")
            print(f"⚠️  Provider created but will fail validation")
        except Exception as e:
            print(f"✅ Provider creation failed as expected: {type(e).__name__}")
            
    except Exception as e:
        print(f"❌ Registry error: {e}")

def test_weaver_initialization():
    """Test Weaver initialization with different configurations."""
    print("\n🔮 Testing Weaver initialization...")
    
    # Test 1: No API key (should fail)
    try:
        weaver = Weaver()
        print(f"❌ Should have failed without API key")
    except WeaverError as e:
        print(f"✅ Failed gracefully without API key: {type(e).__name__}")
    
    # Test 2: With fake API key (should fail validation)
    try:
        weaver = Weaver(api_key="fake_key")
        print(f"⚠️  Created with fake key (validation will fail later)")
    except Exception as e:
        print(f"✅ Failed with fake key: {type(e).__name__}")

def main():
    """Run all tests."""
    print("🧪 Testing Weaver Project Structure")
    print("=" * 40)
    
    test_schema_conversion()
    test_provider_registry()
    test_weaver_initialization()
    
    print("\n🎉 Structure tests completed!")
    print("\n💡 To test with real data generation:")
    print("   1. Set OPENAI_API_KEY environment variable")
    print("   2. Run: uv run python examples/basic_usage.py")

if __name__ == "__main__":
    main()