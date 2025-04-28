from app import create_app
from app.extensions import db
from app.models import User, Product, Category
from werkzeug.security import generate_password_hash

app = create_app()

def seed_data():
    with app.app_context():
        # DROP dan CREATE tabel (jangan pakai kalau sudah produksi ya)
        db.drop_all()
        db.create_all()

        # --- Seed Users ---
        user1 = User(
            name='Ridwan',
            email='ridwan@email.com',
            password_hash=generate_password_hash('password123'),
            role='user'
        )

        owner1 = User(
            name='Yusuf the seller',
            email='yusuf@email.com',
            password_hash=generate_password_hash('password123'),
            role='owner'
        )

        admin1 = User(
            name='Alif the Admin',
            email='alif@email.com',
            password_hash=generate_password_hash('adminpass'),
            role='admin'
        )

        # --- Seed Category ---
        

        category1 = Category(
            name='ELektronic',
            
        )

        # --- Seed Products ---
        elektronik_id = Category.query.filter_by(name="Elektronik").first().id

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
