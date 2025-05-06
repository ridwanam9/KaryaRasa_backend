from flask import Blueprint, request, jsonify, current_app
from app.models import User
from app.extensions import db
from app.utils.auth import token_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import jwt

bp = Blueprint('users', __name__, url_prefix='/users')


# GET /users - Get all users
@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200


# GET /users/<int:id> - Get user by ID
@bp.route('/<int:id>', methods=['GET'])
@token_required
def get_user(current_user, id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict()), 200


# POST /users/register - Register new user
@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        required_fields = ['name', 'email', 'password']
        missing = [f for f in required_fields if not data.get(f)]

        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400

        email = data['email'].strip().lower()

        if User.query.filter_by(email=email).first():
            return jsonify({
                "status": "error",
                "message": "Email is already registered"
            }), 409

        new_user = User(
            name=data['name'].strip(),
            email=email,
            role='user'
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# POST /users/login - User login
@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password')

        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

        token_payload = {
            "user_id": user.id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        }
        token = jwt.encode(token_payload, current_app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "token": token,
            "data": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# DELETE /users/<int:id> - Delete user by ID
@bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_user(current_user, id):
    user = User.query.get_or_404(id)

    # Optional: Allow only self-deletion or admin
    if current_user.id != user.id and current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {user.id} deleted"}), 200


# POST /users/role/switch - Switch user role to seller
@bp.route('/role/switch', methods=['POST'])
@token_required
def switch_role(current_user):
    if current_user.role == 'seller':
        return jsonify({"message": "User is already a seller"}), 200

    if current_user.role != 'user':
        return jsonify({
            "error": "Role switch only allowed from 'user' to 'seller'"
        }), 400

    current_user.role = 'seller'
    db.session.commit()

    return jsonify({
        "message": "User role successfully switched to seller",
        "user": current_user.to_dict()
    }), 200

@bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    # Dummy Logout
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200
