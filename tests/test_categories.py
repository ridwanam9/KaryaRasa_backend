# test/test_categories.py

import pytest
from app import create_app
from app.extensions import db
from app.models import Category

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_get_all_categories(client):
    resp = client.get('/categories/')
    assert resp.status_code == 200
    assert resp.get_json()["status"] in ("success", "error")

def test_create_category_missing_name(client):
    resp = client.post('/categories/', json={})
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Category name is required"

def test_create_category_success(client):
    data = {"name": "Kategori A"}
    resp = client.post('/categories/', json=data)
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "success"
    assert resp.get_json()["data"]["name"] == "Kategori A"

def test_create_category_duplicate(client):
    data = {"name": "Kategori B"}
    # Buat pertama kali
    client.post('/categories/', json=data)
    # Coba buat lagi dengan nama sama
    resp = client.post('/categories/', json=data)
    assert resp.status_code == 409
    assert resp.get_json()["message"] == "Category already exists"

def test_get_category_by_id(client):
    # Buat kategori dulu
    category = Category(name="Kategori C")
    db.session.add(category)
    db.session.commit()
    resp = client.get(f'/categories/{category.id}')
    assert resp.status_code == 200
    assert resp.get_json()["data"]["name"] == "Kategori C"