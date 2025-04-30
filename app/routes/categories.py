from flask import Blueprint, request, jsonify
from app.models import Category, Product
from app.extensions import db

bp = Blueprint('categories', __name__, url_prefix='/categories')

# GET all categories
@bp.route('/', methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify({
            "status": "success",
            "message": "Categories retrieved successfully",
            "data": [category.to_dict() for category in categories]
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# GET category by ID
@bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    try:
        category = Category.query.get_or_404(id)
        return jsonify({
            "status": "success",
            "message": "Category retrieved successfully",
            "data": category.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# POST new category
@bp.route('/', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                "status": "error",
                "message": "Category name is required"
            }), 400

        # Check if category already exists
        if Category.query.filter_by(name=data['name']).first():
            return jsonify({
                "status": "error",
                "message": "Category already exists"
            }), 409

        new_category = Category(name=data['name'])
        db.session.add(new_category)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Category created successfully",
            "data": new_category.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500