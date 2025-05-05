from app.extensions import db
from app.models import User, Category, Product
from werkzeug.security import generate_password_hash

def seed_data():
    # Clear existing data (opsional saat testing)
    db.session.query(Product).delete()
    db.session.query(Category).delete()
    db.session.query(User).delete()

    # Admin
    admin = User(
        id=0,
        name="Admin",
        email="admin@example.com",
        password_hash=generate_password_hash("password"),
        role="admin"
    )

    # Seller
    seller = User(
        name="John Seller",
        email="seller@example.com",
        password_hash=generate_password_hash("password"),
        role="seller"
    )

    # Seller
    user = User(
        name="Ridwan",
        email="ridwan@email.com",
        password_hash=generate_password_hash("password"),
        role="user"
    )

    db.session.add(admin)
    db.session.add(seller)
    db.session.add(user)
    db.session.commit()

    # Categories and sample products
    categories = [
        "Accessories",
        "Art & Collectibles",
        "Clothing",
        "Jewelry",
        "Craft Supplies & Tools",
        "Toys & Games"
    ]

    for name in categories:
        category = Category(name=name)
        db.session.add(category)
        db.session.flush()  # to get category.id

        product = Product(
            name=f"Sample {name}",
            description=f"This is a sample product for {name}.",
            category_id=category.id,
            seller_id=seller.id,
            price=19.99,
            stock=10,
            image_url=f"https://example.com/images/{name.replace(' ', '_').lower()}.jpg"
        )
        db.session.add(product)

    db.session.commit()
    print("✅ Seeder berhasil dijalankan.")
