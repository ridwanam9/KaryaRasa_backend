from flask import Blueprint, request, jsonify
from app.models import db, Transaction, TransactionItem, Product, User, Cart, CartItem, PromoCode
from datetime import datetime, timezone
from flask_jwt_extended import jwt_required, get_jwt_identity
import jwt
from app.utils.auth import token_required

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


@bp.route('/api/cart/items', methods=['GET'])
@token_required
def get_cart_items():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.cart:
        return jsonify({"message": "Cart is empty"}), 200

    cart_items = [item.to_dict() for item in user.cart.cart_items]

    return jsonify({
        "cart_id": user.cart.id,
        "user_id": user.id,
        "cart_items": cart_items
    }), 200


@bp.route('/cart/<int:user_id>', methods=['GET'])
@token_required
def get_user_cart_items(user_id):
    """
    Endpoint untuk admin/seller melihat cart pengguna berdasarkan user_id
    """
    # Dapatkan ID pengguna dari token JWT
    current_user_id = get_jwt_identity()
    
    # Cari user yang sedang login
    current_user = User.query.get(current_user_id)
    if not current_user or current_user.role not in ['admin', 'seller']:
        return jsonify({"error": "Tidak memiliki izin"}), 403
    
    # Cari cart berdasarkan user_id yang diminta
    cart = Cart.query.filter_by(user_id=user_id).first()
    if not cart:
        return jsonify({"error": "Cart tidak ditemukan"}), 404
    
    # Dapatkan semua item dalam cart
    cart_items = CartItem.query.filter_by(cart_id=cart.id).all()
    
    # Buat response yang lebih informatif dengan detail produk
    items_detail = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            items_detail.append({
                "id": item.id,
                "product_id": item.product_id,
                "product_name": product.name,
                "product_price": product.price,
                "quantity": item.quantity,
                "subtotal": product.price * item.quantity
            })
    
    # Hitung total harga
    total_price = sum(item["subtotal"] for item in items_detail)
    
    response = {
        "cart_id": cart.id,
        "user_id": user_id,
        "items": items_detail,
        "total_items": len(items_detail),
        "total_price": total_price
    }
    
    return jsonify(response), 200


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
            seller_name = "Unknown"
            if product.seller_id:
                seller = User.query.get(product.seller_id)
                if seller:
                    seller_name = seller.name

            transaction_item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product.id,
                quantity=item['quantity'],
                price=item['price'],
                product_name=product.name,
                seller_name=seller_name,
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


@bp.route('/seller/orders', methods=['GET'])
@token_required
def get_seller_orders():
    current_user_id = get_jwt_identity()
    seller = User.query.get(current_user_id)

    if seller.role != 'seller':
        return jsonify({"error": "Access denied. Only sellers can access this endpoint."}), 403

    # Ambil semua TransactionItem untuk produk milik seller
    items = (
        db.session.query(TransactionItem, Transaction, User)
        .join(Product, Product.id == TransactionItem.product_id)
        .join(Transaction, Transaction.id == TransactionItem.transaction_id)
        .join(User, User.id == Transaction.user_id)
        .filter(Product.seller_id == seller.id)
        .order_by(Transaction.timestamp.desc())
        .all()
    )

    result = []
    for item, transaction, buyer in items:
        result.append({
            "product_name": item.product_name,
            "buyer_name": buyer.name,
            "quantity": item.quantity,
            "price": float(item.price),
            "subtotal": float(item.price) * item.quantity,
            "payment_status": getattr(transaction, 'payment_status', 'unknown')  # default 'unknown' jika belum ada kolom
        })

    return jsonify(result), 200