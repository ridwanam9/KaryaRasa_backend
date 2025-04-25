from flask import Blueprint, request, jsonify
from app.models import db, Transaction, Product, User

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@bp.route('/', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([t.to_dict() for t in transactions])

@bp.route('/', methods=['POST'])
def create_transaction():
    data = request.get_json()
    user_id = data['user_id']
    product_id = data['product_id']
    quantity = data['quantity']

    product = Product.query.get_or_404(product_id)

    if product.stock < quantity:
        return jsonify({'error': 'Not enough stock'}), 400

    total_price = quantity * product.price
    transaction = Transaction(
        user_id=user_id,
        product_id=product_id,
        quantity=quantity,
        total_price=total_price
    )

    product.stock -= quantity
    db.session.add(transaction)
    db.session.commit()

    return jsonify(transaction.to_dict()), 201

@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_transactions(user_id):
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in transactions])
