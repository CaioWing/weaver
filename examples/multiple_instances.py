"""Example demonstrating multiple instance generation and formatting."""

import os
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from weaver import Weaver


class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str


class User(BaseModel):
    name: str
    email: str
    age: int
    monthly_income: float
    address: Address
    interests: List[str]
    is_premium: bool = False


def demonstrate_single_vs_multiple():
    """Show single vs multiple instance generation."""
    
    # Check for API keys
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not (openrouter_key or openai_key):
        print("❌ Need either OPENROUTER_API_KEY or OPENAI_API_KEY")
        return
    
    # Choose provider
    if openrouter_key:
        weaver = Weaver(provider="openrouter", model="google/gemini-2.5-flash-lite")
        print("🔀 Using OpenRouter with Gemini")
    else:
        weaver = Weaver(provider="openai")
        print("🔵 Using OpenAI directly")
    
    print("\n" + "="*60)
    
    # Example 1: Single instance
    print("\n📝 Example 1: Single User")
    print("-" * 40)
    
    try:
        single_user = weaver.generate(
            model=User,
            prompt="A tech entrepreneur from São Paulo who loves AI and startups",
            temperature=0.2
        )
        
        # Different ways to display results
        print("📊 Summary:")
        print(f"   {Weaver.format_results(single_user, 'summary')}")
        
        print(f"\n👤 Details:")
        print(f"   Name: {single_user.name}")
        print(f"   Email: {single_user.email}")
        print(f"   Age: {single_user.age}")
        print(f"   Income: R$ {single_user.monthly_income:,.2f}")
        print(f"   City: {single_user.address.city}")
        print(f"   Interests: {', '.join(single_user.interests[:3])}...")
        print(f"   Premium: {'Yes' if single_user.is_premium else 'No'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Multiple instances
    print("\n📝 Example 2: Multiple Users")
    print("-" * 40)
    
    try:
        multiple_users = weaver.generate(
            model=User,
            prompt="Diverse Brazilian professionals from different cities and backgrounds",
            count=3,
            temperature=0.3
        )
        
        # Summary view
        print("📊 Summary:")
        print(f"   {Weaver.format_results(multiple_users, 'summary')}")
        
        # Detailed view
        print(f"\n👥 Generated Users:")
        for i, user in enumerate(multiple_users, 1):
            print(f"\n   {i}. {user.name}")
            print(f"      📧 {user.email}")
            print(f"      🎂 {user.age} years old")
            print(f"      💰 R$ {user.monthly_income:,.2f}/month")
            print(f"      🏙️  {user.address.city}, {user.address.state}")
            print(f"      🎯 Interests: {', '.join(user.interests[:2])}...")
        
        # Show JSON for one user
        print(f"\n📄 Sample JSON (User 1):")
        print(multiple_users[0].model_dump_json(indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Large batch
    print("\n📝 Example 3: Large Batch Generation")
    print("-" * 40)
    
    try:
        large_batch = weaver.generate(
            model=User,
            prompt="E-commerce customers from different Brazilian states",
            count=10,
            temperature=0.4
        )
        
        print(f"📊 {Weaver.format_results(large_batch, 'summary')}")
        
        # Analytics
        avg_age = sum(u.age for u in large_batch) / len(large_batch)
        avg_income = sum(u.monthly_income for u in large_batch) / len(large_batch)
        cities = list(set(u.address.city for u in large_batch))
        premium_count = sum(1 for u in large_batch if u.is_premium)
        
        print(f"\n📈 Batch Analytics:")
        print(f"   Average age: {avg_age:.1f} years")
        print(f"   Average income: R$ {avg_income:,.2f}")
        print(f"   Cities represented: {len(cities)}")
        print(f"   Premium users: {premium_count}/{len(large_batch)}")
        
        print(f"\n🏙️  Cities: {', '.join(cities[:5])}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demonstrate_formatting_options():
    """Show different formatting options."""
    
    if not (os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")):
        return
    
    print(f"\n📋 Formatting Options Demo")
    print("=" * 60)
    
    weaver =  Weaver(provider="openrouter", model="google/gemini-2.5-flash-lite")
    
    try:
        users = weaver.generate(
            model=User,
            prompt="Young professionals from Rio de Janeiro",
            count=2
        )
        
        print(f"\n1️⃣  Summary format:")
        print(Weaver.format_results(users, "summary"))
        
        print(f"\n2️⃣  Detailed format:")
        print(Weaver.format_results(users, "detailed"))
        
        print(f"\n3️⃣  JSON format:")
        json_output = Weaver.format_results(users, "json")
        print(json_output[:300] + "..." if len(json_output) > 300 else json_output)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all examples."""
    demonstrate_single_vs_multiple()
    demonstrate_formatting_options()
    
    print(f"\n🎉 Multiple instance examples completed!")
    print(f"\n💡 Tips:")
    print(f"   • Use count=1 for single instances")
    print(f"   • Use count>1 for multiple instances")
    print(f"   • Higher temperature = more diverse results")
    print(f"   • Use Weaver.format_results() for easy display")


if __name__ == "__main__":
    main()