"""Compare different providers and their capabilities."""

import os
import time
from pydantic import BaseModel
from typing import List
from weaver import Weaver


class TestModel(BaseModel):
    name: str
    description: str
    tags: List[str]
    score: float


def test_provider_performance(provider_name: str, model_name: str = None, api_key: str = None):
    """Test a provider's performance and capabilities."""
    print(f"\n🧪 Testing {provider_name.upper()}")
    print("-" * 40)
    
    try:
        # Create Weaver instance
        config = {"provider": provider_name}
        if model_name:
            config["model"] = model_name
        if api_key:
            config["api_key"] = api_key
            
        weaver = Weaver(**config)
        
        # Test prompt
        prompt = "A innovative AI-powered productivity tool for developers"
        
        # Measure generation time
        start_time = time.time()
        result = weaver.generate(
            model=TestModel,
            prompt=prompt,
            temperature=0.2
        )
        generation_time = time.time() - start_time
        
        # Display results
        print(f"✅ Provider: {weaver.provider_name}")
        print(f"⏱️  Generation time: {generation_time:.2f}s")
        print(f"🤖 Model: {weaver.provider_info.get('config', {}).get('model', 'default')}")
        print(f"📄 JSON mode: {weaver.provider_info.get('supports_json_mode', False)}")
        print(f"📝 Generated: {result.name}")
        print(f"   Tags: {', '.join(result.tags[:3])}...")
        print(f"   Score: {result.score}/10")
        
        return {
            "provider": provider_name,
            "success": True,
            "time": generation_time,
            "result": result
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "provider": provider_name, 
            "success": False,
            "error": str(e)
        }


def compare_all_available_providers():
    """Test all configured providers."""
    print("🔍 Provider Capability Comparison")
    print("=" * 60)
    
    # Check available providers
    providers_to_test = []
    
    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        providers_to_test.append(("openai", None, None))
    
    # OpenRouter
    if os.getenv("OPENROUTER_API_KEY"):
        providers_to_test.extend([
            ("openrouter", "openai/gpt-4-turbo", None),
            ("openrouter", "anthropic/claude-3.5-sonnet", None),
            ("openrouter", "google/gemini-pro", None),
        ])
    
    if not providers_to_test:
        print("❌ No API keys found. Set one of:")
        print("   • OPENAI_API_KEY")
        print("   • OPENROUTER_API_KEY")
        return
    
    # Test all providers
    results = []
    for provider, model, api_key in providers_to_test:
        display_name = f"{provider}/{model}" if model else provider
        result = test_provider_performance(provider, model, api_key)
        results.append(result)
    
    # Summary
    print(f"\n📊 Summary")
    print("=" * 60)
    
    successful_tests = [r for r in results if r.get("success")]
    if successful_tests:
        # Sort by speed
        successful_tests.sort(key=lambda x: x.get("time", float('inf')))
        
        print(f"🏆 Fastest: {successful_tests[0]['provider']} ({successful_tests[0]['time']:.2f}s)")
        
        avg_time = sum(r['time'] for r in successful_tests) / len(successful_tests)
        print(f"⏱️  Average time: {avg_time:.2f}s")
        
        print(f"✅ Successful providers: {len(successful_tests)}/{len(results)}")
    
    failed_tests = [r for r in results if not r.get("success")]
    if failed_tests:
        print(f"❌ Failed providers:")
        for test in failed_tests:
            print(f"   • {test['provider']}: {test.get('error', 'Unknown error')}")


def demonstrate_provider_features():
    """Show unique features of each provider."""
    print("\n🎯 Provider Features")
    print("=" * 50)
    
    features = {
        "OpenAI": [
            "🔥 Native JSON mode support",
            "🚀 Fast and reliable",
            "💎 High-quality outputs",
            "💰 Pay-per-token pricing"
        ],
        "OpenRouter": [
            "🌐 Access to multiple model providers",
            "🎛️  Model switching without code changes",
            "💵 Competitive pricing",
            "🔄 Fallback between models",
            "📊 Usage analytics"
        ]
    }
    
    for provider, feature_list in features.items():
        print(f"\n🏢 {provider}:")
        for feature in feature_list:
            print(f"   {feature}")


def main():
    """Run provider comparison."""
    demonstrate_provider_features()
    compare_all_available_providers()
    
    print("\n💡 Tips:")
    print("   • Use OpenAI for reliable, fast generation")
    print("   • Use OpenRouter to access Claude, Gemini, and others")
    print("   • Try different models for different use cases")
    print("   • Set temperature lower (0.1-0.3) for consistent data")


if __name__ == "__main__":
    main()