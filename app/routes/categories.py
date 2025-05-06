from flask import Blueprint, request, jsonify
from app.models import Category
from app.extensions import db

bp = Blueprint('categories', __name__, url_prefix='/categories')


# GET /categories - Get all categories
@bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({
        "status": "success",
        "message": "Categories retrieved successfully",
        "data": [category.to_dict() for category in categories]
    }), 200


# GET /categories/<int:id> - Get category by ID
@bp.route('/<int:id>', methods=['GET'])
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify({
        "status": "success",
        "message": "Category retrieved successfully",
        "data": category.to_dict()
    }), 200


# POST /categories - Create new category
@bp.route('/', methods=['POST'])
def create_category():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()

        if not name:
            return jsonify({
                "status": "error",
                "message": "Category name is required"
            }), 400

        # Check for existing category (case-insensitive)
        existing = Category.query.filter(
            db.func.lower(Category.name) == name.lower()
        ).first()

        if existing:
            return jsonify({
                "status": "error",
                "message": "Category already exists"
            }), 409

        new_category = Category(name=name)
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
