"""Quick test with minimal example."""

from decimal import Decimal
from datetime import datetime
import os
from pydantic import BaseModel
from weaver import Weaver

class SimpleUser(BaseModel):
    name: str
    email: str
    month_income: float
    birth: datetime

def main():
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("💡 Set it with: export OPENAI_API_KEY='your-key-here'")
        return
    
    print("🔮 Testing Weaver with real API...")
    
    try:
        weaver = Weaver(provider="openrouter", model="google/gemini-2.5-flash-image-preview:free")
        print("✅ Weaver initialized successfully")
        
        users = weaver.generate(
            model=SimpleUser,
            prompt="A Brazilian software developer",
            count=5
        )
        
        print(f"✅ Generated {len(users)} users:")
        for i, user in enumerate(users, 1):
            print(f"\n👤 User {i}:")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Income: R$ {user.month_income:,.2f}")
            print(f"   Birth: {user.birth.strftime('%d/%m/%Y')}")
        
        # Optionally, show JSON for first user
        print(f"\n📄 First user as JSON:")
        print(users[0].model_dump_json(indent=2))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()