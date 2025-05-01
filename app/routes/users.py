from flask import Blueprint, request, jsonify
from app.models import User
from app.extensions import db
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.auth import token_required
from datetime import datetime, timedelta, timezone
from flask import current_app
import jwt


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

# Register endpoint - POST /users/register
@bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    "status": "error",
                    "message": f"The {field} field is required"
                }), 400

        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                "status": "error",
                "message": "Email is already registered"
            }), 409

        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'],
            role='user'  # default role
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Registration successful",
            "data": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Login endpoint - POST /users/login
@bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400

        user = User.query.filter_by(email=data['email']).first()

        if user and user.check_password(data['password']):
            token = jwt.encode({
                "user_id": user.id,
                "exp": datetime.now(timezone.utc) + timedelta(hours=1)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            return jsonify({
                "status": "success",
                "message": "Login successful",
                "token": token,
                "data": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Invalid email or password"
            }), 401

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



# DELETE /users/<int:id> → Delete user
@bp.route('/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"User {id} deleted"}), 200


@bp.route('/role/switch', methods=['POST'])
@token_required
def switch_role(current_user):
    if current_user.role == 'seller':
        return jsonify({"message": "User is already a seller"}), 200
    elif current_user.role != 'user':
        return jsonify({"error": "Role switch only allowed from 'user' to 'seller'"}), 400

    current_user.role = 'seller'
    db.session.commit()

    return jsonify({
        "message": "User role successfully switched to seller",
        "user": current_user.to_dict()
    }), 200