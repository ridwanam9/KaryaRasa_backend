# test/test_products.py

import pytest
from app import create_app
from app.extensions import db
from app.models import Product, Category, User

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        # Buat kategori dummy untuk foreign key
        category = Category(name="Test Category")
        db.session.add(category)
        db.session.commit()
        yield app.test_client()
        db.drop_all()

def test_get_all_products(client):
    resp = client.get('/products/')
    assert resp.status_code == 200
    assert isinstance(resp.get_json()["data"], list)

def test_create_product_missing_fields(client):
    resp = client.post('/products/', json={})
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Missing required fields"

def test_create_product_success(client):
    # Ambil id kategori dummy
    category_id = Category.query.first().id
    data = {
        "name": "Produk A",
        "description": "Deskripsi produk",
        "category_id": category_id,
        "seller_id": 1,
        "price": 10000,
        "stock": 10,
        "image_url": "http://example.com/image.jpg"
    }
    resp = client.post('/products/', json=data)
    assert resp.status_code == 201
    assert resp.get_json()["data"]["name"] == "Produk A"

def test_get_product_by_id(client):
    # Buat produk dulu
    category_id = Category.query.first().id
    product = Product(
        name="Produk B",
        description="Deskripsi",
        category_id=category_id,
        seller_id=1,
        price=20000,
        stock=5,
        image_url="http://example.com/img.jpg"
    )
    db.session.add(product)
    db.session.commit()
    resp = client.get(f'/products/{product.id}')
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Produk B"

def test_update_product(client):
    category_id = Category.query.first().id
    product = Product(
        name="Produk C",
        description="Deskripsi",
        category_id=category_id,
        seller_id=1,
        price=30000,
        stock=7,
        image_url="http://example.com/img2.jpg"
    )
    db.session.add(product)
    db.session.commit()
    update_data = {"name": "Produk C Updated"}
    resp = client.put(f'/products/{product.id}', json=update_data)
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Produk C Updated"

def test_delete_product(client):
    category_id = Category.query.first().id
    product = Product(
        name="Produk D",
        description="Deskripsi",
        category_id=category_id,
        seller_id=1,
        price=40000,
        stock=3,
        image_url="http://example.com/img3.jpg"
    )
    db.session.add(product)
    db.session.commit()
    resp = client.delete(f'/products/{product.id}')
    assert resp.status_code == 200
    assert resp.get_json()["message"] == f"Product {product.id} deleted"

def test_add_review_success(client):
    # Buat user dan produk dummy jika belum ada
    if not User.query.first():
        user = User(name="User Review", email="review@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    else:
        user = User.query.first()
    if not Product.query.first():
        category = Category.query.first()
        product = Product(
            name="Produk Review",
            description="Deskripsi",
            category_id=category.id,
            seller_id=user.id,
            price=10000,
            stock=10,
            image_url="http://example.com/img.jpg"
        )
        db.session.add(product)
        db.session.commit()
    else:
        product = Product.query.first()
    data = {"user_id": user.id, "rating": 5, "review": "Bagus!"}
    resp = client.post(f'/products/{product.id}/reviews', json=data)
    assert resp.status_code == 201

def test_add_review_invalid_rating(client):
    # Buat user dan produk dummy jika belum ada
    if not User.query.first():
        user = User(name="User Review", email="review@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    else:
        user = User.query.first()
    if not Product.query.first():
        category = Category.query.first()
        product = Product(
            name="Produk Review",
            description="Deskripsi",
            category_id=category.id,
            seller_id=user.id,
            price=10000,
            stock=10,
            image_url="http://example.com/img.jpg"
        )
        db.session.add(product)
        db.session.commit()
    else:
        product = Product.query.first()
    data = {"user_id": user.id, "rating": 6, "review": "Invalid"}
    resp = client.post(f'/products/{product.id}/reviews', json=data)
    assert resp.status_code == 400

def test_get_reviews(client):
    # Buat produk dummy jika belum ada
    if not Product.query.first():
        if not User.query.first():
            user = User(name="User Review", email="review@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
        else:
            user = User.query.first()
        category = Category.query.first()
        product = Product(
            name="Produk Review",
            description="Deskripsi",
            category_id=category.id,
            seller_id=user.id,
            price=10000,
            stock=10,
            image_url="http://example.com/img.jpg"
        )
        db.session.add(product)
        db.session.commit()
    product = Product.query.first()
    resp = client.get(f'/products/{product.id}/reviews')
    assert resp.status_code == 200
    assert isinstance(resp.get_json()["data"], list)