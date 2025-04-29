from datetime import datetime, timezone
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    password_hash = db.Column(db.Text(), nullable=False)
    role = db.Column(db.String(20), default='user')  # pilihan: 'user', 'owner', 'admin'
    bank_account = db.Column(db.String(255), nullable=True)

    product = db.relationship('Product', backref='user', lazy=True)
    cart = db.relationship('Cart', backref='user', uselist=False, lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date.isoformat() if self.birth_date else None,
            "email": self.email,
            "phone": self.phone,
            "address": self.address
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    products = db.relationship('Product', backref='category', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @staticmethod
    def insert_default_categories():
        default_categories = [
            # Accessories
            "Bags & Purses",
            "Accessories",
            
            # Home & Living
            "Home Decor",
            "Kitchen & Dining",
            "Furniture",
            "Storage & Organization",
            "Pillows & Cushions",
            
            # Art & Collectibles
            "Paintings",
            "Sculptures",
            "Prints",
            
            # Craft Supplies & Tools
            "Beads & Supplies",
            "Craft Tools",
            "Woodworking",
            "Fabric & Textiles",
            
            # Bath & Beauty
            "Bath Accessories",
            "Personal Care",
            
            # Traditional & Cultural
            "Batik",
            "Traditional Weaving",
            "Songket",
            "Cultural Art"
        ]

        for category_name in default_categories:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                new_category = Category(name=category_name)
                db.session.add(new_category)
        
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) #True karena hanya seller saja yang punya produk
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    transactions = db.relationship('Transaction', backref='product', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "detail": self.detail,
            "category": self.category.name if self.category else None,
            "price": self.price,
            "stock": self.stock,
            "image_url": self.image_url
        }


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    cart_items = db.relationship('CartItem', backref='cart', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "cart_items": [item.to_dict() for item in self.cart_items]
        }

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "cart_id": self.cart_id,
            "product_id": self.product_id,
            "quantity": self.quantity
        }

class Transaction(db.Model): #Checkout
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) #nama user yang membayar
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    seller_name = db.Column(db.String(120), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True) # gambar produk
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "seller_name": self.seller_name,
            "product_name": self.product_name,
            "total_price": self.total_price,
            "product_image": self.product_image,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }