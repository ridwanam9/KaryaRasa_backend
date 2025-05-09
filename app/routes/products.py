from flask import Blueprint, request, jsonify
from app.models import Category, Product, ProductReview
from app.extensions import db
from app.utils.auth import token_required

bp = Blueprint('products', __name__, url_prefix='/products')


# GET /products - Get all products
@bp.route('/', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify({
        "status": "success",
        "message": "Products retrieved successfully",
        "data": [p.to_dict() for p in products]
    }), 200


# GET /products/<product_id> - Get product by ID
@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({
        "status": "success",
        "message": "Product retrieved successfully",
        "data": product.to_dict()
    }), 200


# POST /products - Create new product
@bp.route('/', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        category_id = data.get('category_id')
        seller_id = data.get('seller_id')
        price = data.get('price')
        stock = data.get('stock')
        image_url = data.get('image_url', '').strip()

        if not all([name, category_id, price, stock]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        if not Category.query.get(category_id):
            return jsonify({"status": "error", "message": "Category not found"}), 404

        product = Product(
            name=name,
            description=description,
            category_id=category_id,
            seller_id=seller_id,
            price=price,
            stock=stock,
            image_url=image_url
        )
        db.session.add(product)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Product created successfully",
            "data": product.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# PUT /products/<product_id> - Update product
@bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.image_url = data.get('image_url', product.image_url)

    if 'category_id' in data:
        category = Category.query.get(data['category_id'])
        if not category:
            return jsonify({"status": "error", "message": "Category not found"}), 404
        product.category_id = data['category_id']

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Product updated successfully",
        "data": product.to_dict()
    }), 200


# DELETE /products/<product_id> - Delete product
@bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({
        "status": "success",
        "message": f"Product {product_id} deleted"
    }), 200


# GET /products/category/<category_id> - Products by category
@bp.route('/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    products = Product.query.filter_by(category_id=category_id).all()
    return jsonify({
        "status": "success",
        "message": "Products retrieved successfully",
        "data": [p.to_dict() for p in products]
    }), 200


# POST /products/<product_id>/reviews - Add review
@bp.route('/<int:product_id>/reviews', methods=['POST'])
def add_review(product_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        rating = data.get('rating')
        review = data.get('review', '').strip()

        if not all([user_id, rating]):
            return jsonify({"status": "error", "message": "User ID and rating are required"}), 400

        if not (1 <= rating <= 5):
            return jsonify({"status": "error", "message": "Rating must be between 1 and 5"}), 400

        new_review = ProductReview(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            review=review
        )
        db.session.add(new_review)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Review added successfully"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


# GET /products/<product_id>/reviews - Get reviews for a product
@bp.route('/<int:product_id>/reviews', methods=['GET'])
def get_reviews(product_id):
    reviews = ProductReview.query.filter_by(product_id=product_id).all()
    return jsonify({
        "status": "success",
        "message": "Reviews retrieved successfully",
        "data": [{
            "user_id": r.user_id,
            "rating": r.rating,
            "review": r.review,
            "created_at": r.created_at
        } for r in reviews]
    }), 200


# GET /products/seller/<int:seller_id> - Ambil produk berdasarkan seller
@bp.route('/seller/<int:seller_id>', methods=['GET'])
@token_required
def get_products_by_seller(seller_id):
    try:
        # Langsung ambil produk berdasarkan seller_id
        products = Product.query.filter_by(seller_id=seller_id).all()
        
        return jsonify({
            "status": "success",
            "message": "Daftar produk seller berhasil diambil",
            "data": [product.to_dict() for product in products]
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
