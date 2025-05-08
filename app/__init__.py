# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from config import Config

# db = SQLAlchemy()

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)

#     db.init_app(app)

#     from app.routes import users, products, transactions
#     app.register_blueprint(users.bp)
#     app.register_blueprint(products.bp)
#     app.register_blueprint(transactions.bp)

#     with app.app_context():
#         db.create_all()

#     return app

from flask import Flask
from config import Config
from app.extensions import db, migrate
from flask_cors import CORS
from dotenv import load_dotenv



def create_app(testing=False):
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    # Konfigurasi CORS setelah app selesai di-setup
    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    CORS(app,
    origins=["https://karyarasa.netlify.app/"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])


    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import users, products, transactions, categories
    app.register_blueprint(users.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(transactions.bp)
    app.register_blueprint(categories.bp)

    from app import models

    with app.app_context():
        db.create_all()

    return app