import os
import jwt
from flask import request, jsonify
from functools import wraps
from app.models import User
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Secret key for JWT
SECRET_KEY = os.getenv('SECRET_KEY')

def token_required(func):
    """
    Decorator to protect routes with JWT authentication.
    It extracts and validates the token from the Authorization header.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Allow CORS preflight request without token
        if request.method == 'OPTIONS':
            return '', 200

        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            return jsonify({'message': 'Token is missing!'}), 401

        token_parts = auth_header.split()
        token = token_parts[1] if len(token_parts) == 2 and token_parts[0].lower() == 'bearer' else None

        if not token:
            return jsonify({'message': 'Token format is invalid!'}), 401

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(payload.get('user_id'))

            if not current_user:
                return jsonify({'message': 'User not found'}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': f'Token validation error: {str(e)}'}), 500

        return func(current_user, *args, **kwargs)

    return wrapper
