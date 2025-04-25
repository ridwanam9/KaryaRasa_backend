from app import create_app
from app.extensions import db
from app.models import User, Product, Transaction
from datetime import datetime, timezone
import random


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Seed Users
    user1 = User(name='Alice', email='alice@email.com')
    user1.set_password('password')

    user2 = User(name='Bob', email='bob@email.com')
    user2.set_password('password')

    db.session.add_all([user1, user2])
    db.session.commit()

    # Seed Products
    product1 = Product(name='Organic Rice', description='Healthy rice from local farms', price=10.5, stock=100)
    product2 = Product(name='Reusable Bag', description='Eco-friendly shopping bag', price=3.99, stock=50)

    db.session.add_all([product1, product2])
    db.session.commit()

    # Seed Transactions
    transaction1 = Transaction(user_id=user1.id, product_id=product1.id, quantity=2, total_price=21.0)
    transaction2 = Transaction(user_id=user2.id, product_id=product2.id, quantity=5, total_price=19.95)

    db.session.add_all([transaction1, transaction2])
    db.session.commit()

    print("✅ Seeding completed.")
