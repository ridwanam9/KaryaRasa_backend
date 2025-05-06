# test/test_users.py

import pytest
from app import create_app
from app.extensions import db
from app.models import User

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def test_get_all_users(client):
    resp = client.get('/users/')
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)

def test_register_missing_fields(client):
    resp = client.post('/users/register', json={})
    assert resp.status_code == 400
    assert resp.get_json()["message"].startswith("Missing required fields")

def test_register_success(client):
    data = {
        "name": "User A",
        "email": "usera@example.com",
        "password": "password123"
    }
    resp = client.post('/users/register', json=data)
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "success"
    assert resp.get_json()["data"]["email"] == "usera@example.com"

def test_register_duplicate_email(client):
    data = {
        "name": "User B",
        "email": "userb@example.com",
        "password": "password123"
    }
    # Register pertama
    client.post('/users/register', json=data)
    # Register kedua dengan email sama
    resp = client.post('/users/register', json=data)
    assert resp.status_code == 409
    assert resp.get_json()["message"] == "Email is already registered"

def test_login_missing_fields(client):
    resp = client.post('/users/login', json={})
    assert resp.status_code == 400
    assert resp.get_json()["message"] == "Email and password are required"

def test_login_invalid(client):
    data = {
        "email": "notfound@example.com",
        "password": "wrongpass"
    }
    resp = client.post('/users/login', json=data)
    assert resp.status_code == 401
    assert resp.get_json()["message"] == "Invalid email or password"

def test_login_success(client):
    # Register user dulu
    reg_data = {
        "name": "User C",
        "email": "userc@example.com",
        "password": "password123"
    }
    client.post('/users/register', json=reg_data)
    login_data = {
        "email": "userc@example.com",
        "password": "password123"
    }
    resp = client.post('/users/login', json=login_data)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "success"
    assert "token" in resp.get_json()

def test_get_user_by_id(client):
    # Register user dulu
    reg_data = {
        "name": "User D",
        "email": "userd@example.com",
        "password": "password123"
    }
    reg_resp = client.post('/users/register', json=reg_data)
    user_id = reg_resp.get_json()["data"]["id"]
    # Login untuk dapatkan token
    login_data = {
        "email": "userd@example.com",
        "password": "password123"
    }
    login_resp = client.post('/users/login', json=login_data)
    token = login_resp.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get(f'/users/{user_id}', headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "User D"

def test_delete_user(client):
    # Register user dulu
    reg_data = {
        "name": "User E",
        "email": "usere@example.com",
        "password": "password123"
    }
    reg_resp = client.post('/users/register', json=reg_data)
    user_id = reg_resp.get_json()["data"]["id"]
    # Login untuk dapatkan token
    login_data = {
        "email": "usere@example.com",
        "password": "password123"
    }
    login_resp = client.post('/users/login', json=login_data)
    token = login_resp.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.delete(f'/users/{user_id}', headers=headers)
    assert resp.status_code == 200
    assert "deleted" in resp.get_json()["message"]