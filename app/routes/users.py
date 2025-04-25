from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from werkzeug.security import check_password_hash

bp = Blueprint('users', __name__, url_prefix='/users')

# GET /users → Get all users
@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

# GET /users/<int:id> → Get user by ID
@bp.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200

# POST /users/login → Login user
@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password_hash, password):
        return jsonify({"message": "Login successful", "user": user.to_dict()}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401


# POST /users → Create new user
@bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(
        name=data['name'],
        email=data['email'],
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201


# # PUT /users/<int:id> → Update user
# @bp.route('/<int:id>', methods=['PUT'])
# def update_user(id):
#     user = User.query.get_or_404(id)
#     data = request.get_json()

#     user.name = data.get('name', user.name)
#     user.email = data.get('email', user.email)
#     user.password = data.get('password', user.password)

#     db.session.commit()
#     return jsonify(user.to_dict()), 200

# there is an error far update user, will fix it later

# DELETE /users/<int:id> → Delete user
@bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {id} deleted"}), 200
