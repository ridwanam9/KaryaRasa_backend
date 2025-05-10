from flask import Blueprint, request, jsonify
from app.models import Category, Product, ProductReview
from app.extensions import db
from app.utils.auth import token_required
from werkzeug.utils import secure_filename
import uuid
from supabase import create_client, Client
from supabase_client import supabase, SUPABASE_URL

bp = Blueprint('products', __name__, url_prefix='/products')



# Helper function to validate price and stock
def validate_price_and_stock(price, stock):
    try:
        price = float(price)
        stock = int(stock)
        if price <= 0 or stock < 0:
            raise ValueError("Price must be positive and stock must be a non-negative integer.")
        return price, stock
    except ValueError as e:
        return None, str(e)


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
@bp.route('/', methods=['POST', 'OPTIONS'])
@token_required
def create_product(current_user):
    if request.method == "OPTIONS":
        # Menangani preflight request
        return '', 200
    if current_user.role != 'seller':
        return jsonify({"status": "error", "message": "Only sellers can add products"}), 403

    # Get data from the request
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    category_id = request.form.get('category_id')
    price = request.form.get('price')
    stock = request.form.get('stock')
    image = request.files.get('image')

    # Check if all required fields are provided
    if not all([name, category_id, price, stock, image]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Validate category
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"status": "error", "message": "Category not found"}), 404

    # Validate price and stock
    price, price_error = validate_price_and_stock(price, stock)
    if price is None:
        return jsonify({"status": "error", "message": price_error}), 400

    # Upload the image to Supabase Storage
    try:
        filename = f"{uuid.uuid4().hex}_{secure_filename(image.filename)}"
        response = supabase.storage.from_('product-images').upload(filename, image, {"content-type": image.content_type})
        if response.get('status_code') != 200:
            raise Exception("Failed to upload image to Supabase Storage.")
        image_url = f"{SUPABASE_URL}/storage/v1/object/public/product-images/{filename}"
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error uploading image: {str(e)}"}), 500

    # Create the new product
    product = Product(
        name=name,
        description=description,
        category_id=category_id,
        seller_id=current_user.id,
        price=price,
        stock=stock,
        image_url=image_url
    )

    # Save the product to the database
    try:
        db.session.add(product)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error saving product: {str(e)}"}), 500

    return jsonify({
        "status": "success",
        "message": "Product created successfully",
        "data": product.to_dict()
    }), 201


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
