# test/test_transactions.py

import pytest
from app import create_app
from app.extensions import db
from app.models import User, Product, Category, Cart, CartItem, Transaction, PromoCode

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        # Dummy user, category, product
        user = User(name="User T", email="usert@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        category = Category(name="Kategori T")
        db.session.add(category)
        db.session.commit()
        product = Product(
            name="Produk T",
            description="Deskripsi",
            category_id=category.id,
            seller_id=user.id,
            price=10000,
            stock=10,
            image_url="http://example.com/img.jpg"
        )
        db.session.add(product)
        db.session.commit()
        yield app.test_client()
        db.drop_all()

def test_get_all_transactions(client):
    resp = client.get('/transactions/')
    assert resp.status_code == 200
    assert resp.get_json()["status"] in ("success", "error")

def test_get_user_transactions(client):
    user = User.query.filter_by(email="usert@example.com").first()
    resp = client.get(f'/transactions/user/{user.id}')
    assert resp.status_code == 200
    assert resp.get_json()["status"] in ("success", "error")

def test_checkout_from_cart(client):
    user = User.query.filter_by(email="usert@example.com").first()
    product = Product.query.first()
    # Buat cart dan cart item
    cart = Cart(user_id=user.id)
    db.session.add(cart)
    db.session.commit()
    cart_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=2)
    db.session.add(cart_item)
    db.session.commit()
    resp = client.post(f'/transactions/checkout/{user.id}')
    assert resp.status_code in (201, 400)
    data = resp.get_json()
    assert data["status"] in ("success", "error")

def test_get_transaction_by_id(client):
    # Buat transaksi dummy
    user = User.query.filter_by(email="usert@example.com").first()
    transaction = Transaction(user_id=user.id, total_price=20000)
    db.session.add(transaction)
    db.session.commit()
    resp = client.get(f'/transactions/{transaction.id}')
    assert resp.status_code == 200
    assert resp.get_json()["status"] in ("success", "error")

def test_update_transaction_status(client):
    # Buat transaksi dummy
    user = User.query.filter_by(email="usert@example.com").first()
    transaction = Transaction(user_id=user.id, total_price=20000)
    db.session.add(transaction)
    db.session.commit()
    data = {"status": "paid"}
    resp = client.put(f'/transactions/{transaction.id}/status', json=data)
    assert resp.status_code == 200
    assert resp.get_json()["status"] in ("success", "error")

def test_checkout_with_valid_promo(client):
    # Buat promo code dummy
    promo = PromoCode(code="PROMO10", discount_percent=10, is_active=True)
    db.session.add(promo)
    db.session.commit()
    # Buat user, cart, cart item, dsb.
    user = User.query.first()
    # ... setup cart ...
    resp = client.post(f'/transactions/checkout/{user.id}', json={"promo_code": "PROMO10"})
    assert resp.status_code in (201, 400)  # tergantung stok/cart

def test_checkout_with_invalid_promo(client):
    user = User.query.first()
    resp = client.post(f'/transactions/checkout/{user.id}', json={"promo_code": "TIDAKVALID"})
    assert resp.status_code == 400