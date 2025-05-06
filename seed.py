from app import create_app
from app.extensions import db
from app.models import User, Category, Product, ProductReview, Cart, CartItem, Transaction, TransactionItem
from datetime import date
from werkzeug.security import generate_password_hash
import random

app = create_app()

def seed_data():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # === USERS ===
        admin = User(
            id=0,
            name="Admin User",
            email="admin@example.com",
            password_hash=generate_password_hash("password"),
            role="admin"
        )
        seller = User(
            name="Seller One",
            email="seller@example.com",
            password_hash=generate_password_hash("password"),
            role="seller"
        )
        user1 = User(
            name="Ridwan",
            email="ridwan@email.com",
            password_hash=generate_password_hash("password"),
            role="user"
        )
        user2 = User(
            name="Rio",
            email="rio@email.com",
            password_hash=generate_password_hash("password"),
            role="user"
        )
        user3 = User(
            name="Tere",
            email="tere@email.com",
            password_hash=generate_password_hash("password"),
            role="user"
        )

        db.session.add_all([admin, seller, user1, user2, user3])
        db.session.commit()

        users = [user1, user2, user3]

        # === CATEGORIES ===
        cat1 = Category(name="Pangan")
        cat2 = Category(name="Kerajinan")
        cat3 = Category(name="Kesehatan")
        db.session.add_all([cat1, cat2, cat3])
        db.session.commit()

        # === CATEGORIES ===
        cat1 = Category(name="Accessories")
        cat2 = Category(name="Art & Collectibles")
        cat3 = Category(name="Clothing")
        cat4 = Category(name="Jewelry")
        cat5 = Category(name="Craft Supplies & Tools")
        cat6 = Category(name="Toys & Games")

        db.session.add_all([cat1, cat2, cat3, cat4, cat5, cat6])
        db.session.commit()

        # === PRODUCTS ===
        product1 = Product(
            name="Handmade Leather Wallet",
            description="Genuine leather wallet with personalized engraving.",
            category_id=cat1.id,
            seller_id=seller.id,
            price=150000,
            stock=50,
            image_url="https://via.placeholder.com/150"
        )
        product2 = Product(
            name="Abstract Painting",
            description="Original acrylic painting on canvas.",
            category_id=cat2.id,
            seller_id=seller.id,
            price=300000,
            stock=10,
            image_url="https://via.placeholder.com/150"
        )
        product3 = Product(
            name="Knitted Wool Sweater",
            description="Warm and cozy handmade sweater.",
            category_id=cat3.id,
            seller_id=seller.id,
            price=250000,
            stock=25,
            image_url="https://via.placeholder.com/150"
        )
        product4 = Product(
            name="Silver Pendant Necklace",
            description="Sterling silver necklace with gemstone.",
            category_id=cat4.id,
            seller_id=seller.id,
            price=200000,
            stock=30,
            image_url="https://via.placeholder.com/150"
        )
        product5 = Product(
            name="DIY Candle Making Kit",
            description="Complete set for making scented candles.",
            category_id=cat5.id,
            seller_id=seller.id,
            price=175000,
            stock=20,
            image_url="https://via.placeholder.com/150"
        )
        product6 = Product(
            name="Wooden Puzzle Toy",
            description="Eco-friendly brain teaser for kids.",
            category_id=cat6.id,
            seller_id=seller.id,
            price=80000,
            stock=60,
            image_url="https://via.placeholder.com/150"
        )

        db.session.add_all([product1, product2, product3, product4, product5, product6])
        db.session.commit()

        products = [product1, product2, product3, product4, product5, product6]

        # === REVIEWS ===
        for user in users:
            for product in products[:3]:
                review = ProductReview(
                    product_id=product.id,
                    user_id=user.id,
                    rating=random.randint(3, 5),
                    review=f"Bagus banget, saya suka {product.name}"
                )
                db.session.add(review)
        db.session.commit()

        # === CART & CART ITEMS ===
        for user in users:
            cart = Cart(user_id=user.id)
            db.session.add(cart)
            db.session.commit()

            for product in products[:2]:
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product.id,
                    quantity=random.randint(1, 3)
                )
                db.session.add(cart_item)
        db.session.commit()

        # === TRANSACTIONS & TRANSACTION ITEMS ===
        for user in users:
            transaction = Transaction(user_id=user.id, total_price=0)
            db.session.add(transaction)
            db.session.commit()

            total = 0
            for product in products[:2]:
                qty = random.randint(1, 2)
                subtotal = float(product.price) * qty
                total += subtotal

                t_item = TransactionItem(
                    transaction_id=transaction.id,
                    product_id=product.id,
                    quantity=qty,
                    price=product.price,
                    image_url=product.image_url,
                    product_name=product.name,
                    seller_name=product.seller.name
                )
                db.session.add(t_item)

            transaction.total_price = total
            db.session.commit()

        print("✅ Seeding completed!")

if __name__ == '__main__':
    seed_data()
