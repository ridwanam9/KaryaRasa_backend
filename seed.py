from app import create_app
from app.extensions import db
from app.models import User, Product
from werkzeug.security import generate_password_hash

app = create_app()

def seed_data():
    with app.app_context():
        # DROP dan CREATE tabel (jangan pakai kalau sudah produksi ya)
        db.drop_all()
        db.create_all()

        # --- Seed Users ---
        user1 = User(
            name='Alice',
            email='alice@example.com',
            password_hash=generate_password_hash('password123'),
            role='user'
        )

        owner1 = User(
            name='Bob the Seller',
            email='bob@example.com',
            password_hash=generate_password_hash('password123'),
            role='owner'
        )

        admin1 = User(
            name='Charlie the Admin',
            email='charlie@example.com',
            password_hash=generate_password_hash('adminpass'),
            role='admin'
        )

        # --- Seed Products ---
        product1 = Product(
            name='Laptop Gaming',
            description='Laptop gaming high performance untuk main game AAA.',
            price=1500.00,
            stock=10
        )

        product2 = Product(
            name='Headset Wireless',
            description='Headset bluetooth kualitas premium.',
            price=200.00,
            stock=25
        )

        product3 = Product(
            name='Mouse Mechanical',
            description='Mouse dengan switch clicky premium.',
            price=80.00,
            stock=40
        )

        # Masukkan ke database
        db.session.add_all([user1, owner1, admin1, product1, product2, product3])
        db.session.commit()

        print("✅ Database berhasil di-seed dengan role!")

if __name__ == "__main__":
    seed_data()
