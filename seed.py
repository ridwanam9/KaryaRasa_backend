# from app import create_app
# from app.extensions import db
# from app.models import User, Product, Transaction
# from datetime import datetime, timezone
# import random

from app.extensions import db
from app.models import User, Product
from werkzeug.security import generate_password_hash

def seed_data():
    # Hapus data lama (hati-hati kalau sudah ada data penting!)
    db.drop_all()
    db.create_all()

    # Seed User (konsumen biasa)
    user1 = User(
        name='Alice',
        email='alice@example.com',
        password_hash=generate_password_hash('password123')
    )
    
    # Seed Owner/Produsen (misal kita tandai sebagai user biasa juga)
    owner1 = User(
        name='Bob the Seller',
        email='bob@example.com',
        password_hash=generate_password_hash('password123')
    )

    # Seed Admin (kalau mau beda, bisa tambah role di tabel User nanti)
    admin1 = User(
        name='Charlie the Admin',
        email='charlie@example.com',
        password_hash=generate_password_hash('adminpass')
    )

    # Seed Product
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

    # Tambahkan ke session
    db.session.add_all([user1, owner1, admin1, product1, product2, product3])
    
    # Commit ke database
    db.session.commit()

    print("✅ Database berhasil di-seed!")

