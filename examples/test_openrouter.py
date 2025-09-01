"""Test OpenRouter provider without requiring API key."""

import os
from pydantic import BaseModel
from weaver import Weaver, WeaverError
from weaver.providers.openrouter_provider import OpenRouterProvider


class SimpleModel(BaseModel):
    name: str
    value: int


def test_openrouter_features():
    """Test OpenRouter provider features."""
    print("🔀 Testing OpenRouter Provider Features")
    print("=" * 50)
    
    # Test 1: Model recommendations
    print("\n🎯 Model Recommendations:")
    use_cases = ["general", "fast", "creative", "code", "budget"]
    for use_case in use_cases:
        model = OpenRouterProvider.get_recommended_model(use_case)
        print(f"   {use_case}: {model}")
    
    # Test 2: Available models
    print(f"\n📋 Available Models:")
    models = OpenRouterProvider.get_available_models()
    for provider, model_list in models.items():
        print(f"   {provider}: {len(model_list)} models")
    
    # Test 3: JSON mode support
    print(f"\n✅ JSON Mode Support:")
    test_models = [
        "openai/gpt-4-turbo",
        "anthropic/claude-3.5-sonnet", 
        "google/gemini-pro",
        "meta-llama/llama-3.1-8b-instruct"
    ]
    
    for model in test_models:
        supports_json = model in OpenRouterProvider.JSON_MODE_MODELS
        icon = "✅" if supports_json else "⚠️"
        print(f"   {icon} {model}")
    
    # Test 4: Provider initialization (without API key)
    print(f"\n🔧 Provider Initialization:")
    try:
        provider = OpenRouterProvider(api_key="fake_key")
        print(f"   ✅ Created OpenRouter provider")
        print(f"   📝 Name: {provider.name}")
        print(f"   🤖 Model: {provider.model}")
        print(f"   🔗 Base URL: {provider.base_url}")
    except Exception as e:
        print(f"   ⚠️  Creation failed: {e}")
    
    # Test 5: Weaver integration
    print(f"\n🔮 Weaver Integration:")
    try:
        weaver = Weaver(provider="openrouter", api_key="fake_key")
        print(f"   ❌ Should have failed with fake key")
    except WeaverError as e:
        print(f"   ✅ Failed gracefully: {type(e).__name__}")
    
    # Test 6: Check environment
    print(f"\n🌍 Environment Check:")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"   OPENROUTER_API_KEY: {'✅ Set' if openrouter_key else '❌ Not set'}")
    print(f"   OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    
    if not (openrouter_key or openai_key):
        print(f"\n💡 To test with real generation:")
        print(f"   • OpenRouter: Get free key at https://openrouter.ai/keys")
        print(f"   • Set: export OPENROUTER_API_KEY='your-key'")
        print(f"   • Run: uv run python examples/openrouter_examples.py")


def test_quick_generation():
    """Test generation if API key is available."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print(f"\n⏭️  Skipping generation test (no OPENROUTER_API_KEY)")
        return
    
    print(f"\n🚀 Testing Real Generation with OpenRouter")
    print("=" * 50)
    
    try:
        # Test with different models
        models_to_test = [
            "openai/gpt-4-turbo",
            "anthropic/claude-3.5-sonnet"
        ]
        
        for model in models_to_test[:1]:  # Test just one to avoid rate limits
            try:
                print(f"\n🤖 Testing {model}:")
                weaver = Weaver(
                    provider="openrouter",
                    model=model,
                    temperature=0.1
                )
                
                result = weaver.generate(
                    model=SimpleModel,
                    prompt="A Brazilian startup focused on AI"
                )
                
                print(f"   ✅ Generated: {result.name} (value: {result.value})")
                
            except Exception as e:
                print(f"   ❌ Error with {model}: {e}")
                
    except Exception as e:
        print(f"❌ Generation test failed: {e}")


def main():
    """Run all OpenRouter tests."""
    test_openrouter_features()
    test_quick_generation()
    
    print(f"\n🎉 OpenRouter tests completed!")


if __name__ == "__main__":
    main()