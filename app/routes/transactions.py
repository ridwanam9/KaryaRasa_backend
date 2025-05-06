from flask import Blueprint, request, jsonify
from app.models import db, Transaction, TransactionItem, Product, User, Cart, CartItem, PromoCode
from datetime import datetime, timezone

bp = Blueprint('transactions', __name__, url_prefix='/transactions')

# Utility function: calculate total price and check stock
def process_cart_items(cart_items):
    total_price = 0
    items_to_process = []
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        if not product:
            raise ValueError(f"Produk dengan ID {cart_item.product_id} tidak ditemukan")
        if product.stock < cart_item.quantity:
            raise ValueError(f"Stok tidak cukup untuk produk {product.name}")
        subtotal = product.price * cart_item.quantity
        total_price += subtotal
        items_to_process.append({
            'product': product,
            'quantity': cart_item.quantity,
            'price': product.price
        })
    return total_price, items_to_process

# Utility function: apply promo code
def apply_promo_code(code_str, total_price):
    promo = PromoCode.query.filter_by(code=code_str, is_active=True).first()
    if not promo:
        raise ValueError("Promo code is invalid or inactive")
    if promo.discount_percent:
        return total_price * (promo.discount_percent / 100)
    elif promo.discount_amount:
        return promo.discount_amount
    return 0

@bp.route('/', methods=['GET'])
def get_transactions():
    try:
        transactions = Transaction.query.all()
        return jsonify({
            "status": "success",
            "message": "Transaksi berhasil diambil",
            "data": [t.to_dict() for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_transactions(user_id):
    try:
        user = User.query.get_or_404(user_id)
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        return jsonify({
            "status": "success",
            "message": "Transaksi user berhasil diambil",
            "data": [t.to_dict() for t in transactions]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/checkout/<int:user_id>', methods=['POST'])
def checkout_from_cart(user_id):
    try:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if not cart or not cart.cart_items:
            return jsonify({"status": "error", "message": "Keranjang kosong"}), 400

        total_price, items_to_process = process_cart_items(cart.cart_items)
        discount = 0

        promo_code_str = request.json.get('promo_code')
        if promo_code_str:
            try:
                discount = apply_promo_code(promo_code_str, total_price)
            except ValueError as e:
                return jsonify({"status": "error", "message": str(e)}), 400

        total_price = max(total_price - discount, 0)

        transaction = Transaction(
            user_id=user_id,
            total_price=total_price,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(transaction)
        db.session.flush()

        for item in items_to_process:
            product = item['product']
            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product.id,
                quantity=item['quantity'],
                price=item['price'],
                product_name=product.name,
                seller_name=product.user.name if product.user else "Unknown",
                image_url=product.image_url
            )
            product.stock -= item['quantity']
            db.session.add(transaction_item)

        for item in cart.cart_items:
            db.session.delete(item)
        db.session.delete(cart)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Checkout berhasil",
            "data": transaction.to_dict()
        }), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    try:
        transaction = Transaction.query.get_or_404(transaction_id)
        return jsonify({
            "status": "success",
            "message": "Detail transaksi berhasil diambil",
            "data": transaction.to_dict()
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/<int:transaction_id>/status', methods=['PUT'])
def update_transaction_status(transaction_id):
    try:
        data = request.get_json()
        if 'status' not in data:
            return jsonify({"status": "error", "message": "Status transaksi diperlukan"}), 400

        transaction = Transaction.query.get_or_404(transaction_id)
        transaction.status = data['status']

        if 'payment_proof' in data:
            transaction.payment_proof = data['payment_proof']

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Status transaksi berhasil diupdate",
            "data": transaction.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
