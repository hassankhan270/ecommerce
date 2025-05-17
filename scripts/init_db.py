import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.session import engine, Base
from app.models.models import Category, Product, Inventory, Sale, InventoryHistory
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    session = Session(engine)
    
    try:
        # Create sample categories
        categories = [
            Category(name="Electronics", description="Electronic devices and accessories"),
            Category(name="Clothing", description="Apparel and fashion items"),
            Category(name="Books", description="Books and publications"),
            Category(name="Home & Kitchen", description="Home and kitchen appliances"),
            Category(name="Sports", description="Sports equipment and accessories")
        ]
        session.add_all(categories)
        session.commit()
        
        # Create sample products
        products = []
        for category in categories:
            for i in range(5):  # 5 products per category
                product = Product(
                    name=f"{category.name} Product {i+1}",
                    description=f"Description for {category.name} Product {i+1}",
                    price=round(random.uniform(10.0, 1000.0), 2),
                    category_id=category.id
                )
                products.append(product)
        
        session.add_all(products)
        session.commit()
        
        # Create inventory for each product
        inventory_items = []
        for product in products:
            inventory = Inventory(
                product_id=product.id,
                quantity=random.randint(0, 100),
                low_stock_threshold=10
            )
            inventory_items.append(inventory)
        
        session.add_all(inventory_items)
        session.commit()
        
        # Create sample sales
        sales = []
        for product in products:
            # Create sales for the last 30 days
            for i in range(30):
                if random.random() < 0.3:  # 30% chance of a sale each day
                    quantity = random.randint(1, 5)
                    sale = Sale(
                        product_id=product.id,
                        quantity=quantity,
                        total_amount=round(product.price * quantity, 2),
                        sale_date=datetime.utcnow() - timedelta(days=i)
                    )
                    sales.append(sale)
        
        session.add_all(sales)
        session.commit()
        
        # Create inventory history
        history_items = []
        for inventory in inventory_items:
            # Create some random inventory changes
            current_quantity = inventory.quantity
            for i in range(5):
                new_quantity = random.randint(0, 100)
                history = InventoryHistory(
                    inventory_id=inventory.id,
                    previous_quantity=current_quantity,
                    new_quantity=new_quantity,
                    change_reason=f"Stock adjustment {i+1}",
                    change_date=datetime.utcnow() - timedelta(days=i*7)
                )
                history_items.append(history)
                current_quantity = new_quantity
        
        session.add_all(history_items)
        session.commit()
        
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db() 