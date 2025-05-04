from flask import Blueprint, request, jsonify
from app.models import Category, Product
from app.extensions import db


bp = Blueprint('products', __name__, url_prefix='/products')


@bp.route('/', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@bp.route('/', methods=['POST'])
def create_product():
    data = request.get_json()

    name = data.get('name')
    description = data.get('description')
    category_id = data.get('category_id')
    seller_id = data.get('seller_id')
    price = data.get('price')
    stock = data.get('stock')
    image_url = data.get('image_url')

    if not all([name, category_id, price, stock]):
        return jsonify({"message": "Missing required fields"}), 400

    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404

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
    return jsonify(product.to_dict()), 201


@bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)
    product.image_url = data.get('image_url', product.image_url)

    category_id = data.get('category_id')
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"message": "Category not found"}), 404
        product.category_id = category_id

    db.session.commit()
    return jsonify(product.to_dict()), 200


@bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


@bp.route('/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"message": "Category not found"}), 404

    products = Product.query.filter_by(category_id=category_id).all()
    return jsonify([p.to_dict() for p in products]), 200