"""Basic usage example for Weaver library."""

from pydantic import BaseModel
from typing import List
from weaver import Weaver


# Define your Pydantic models
class Order(BaseModel):
    product_id: int
    quantity: int
    price: float


class User(BaseModel):
    name: str
    email: str
    age: int
    orders: List[Order]


def main():
    """Demonstrate basic Weaver usage."""
    # Initialize Weaver (will use OPENAI_API_KEY environment variable)
    weaver = Weaver()
    
    print("🔮 Weaver - Generate realistic test data with AI")
    print("=" * 50)
    
    # Example 1: Single user
    print("\n📝 Example 1: Generate a single user")
    try:
        user = weaver.generate(
            model=User,
            prompt="A 25-year-old user named João who made 2 orders of different products"
        )
        
        if isinstance(user, list):
            print(f"Generated {len(user)} users:")
            for u in user:
                print(f"  • {u.name} ({u.email}) - {len(u.orders)} orders")
        else:
            print(f"Generated User: {user.model_dump_json(indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Multiple users
    print("\n📝 Example 2: Generate multiple users")
    try:
        users = weaver.generate(
            model=User,
            prompt="E-commerce customers from Brazil, ages 20-40",
            count=3
        )
        
        print(f"Generated {len(users)} users:")
        for i, user in enumerate(users, 1):
            print(f"User {i}: {user.name} ({user.email}) - {len(user.orders)} orders")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Specific scenario
    print("\n📝 Example 3: Specific business scenario")
    try:
        vip_user = weaver.generate(
            model=User,
            prompt="A VIP customer who has made high-value purchases (orders over $100)"
        )
        
        print(f"VIP Customer: {vip_user.name}")
        print(f"Total orders: {len(vip_user.orders)}")
        total_spent = sum(order.price * order.quantity for order in vip_user.orders)
        print(f"Total spent: ${total_spent:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()