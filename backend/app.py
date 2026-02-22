import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from config import SECRET_KEY, DATABASE_PATH, JWT_EXPIRATION_HOURS
from models import db

jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=JWT_EXPIRATION_HOURS)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from routes import auth, products, suppliers, customers, purchases, sales, inventory, categories, units
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(products.bp, url_prefix='/api/products')
    app.register_blueprint(suppliers.bp, url_prefix='/api/suppliers')
    app.register_blueprint(customers.bp, url_prefix='/api/customers')
    app.register_blueprint(purchases.bp, url_prefix='/api/purchases')
    app.register_blueprint(sales.bp, url_prefix='/api/sales')
    app.register_blueprint(inventory.bp, url_prefix='/api/inventory')
    app.register_blueprint(categories.bp, url_prefix='/api/categories')
    app.register_blueprint(units.bp, url_prefix='/api/units')

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Claw ERP API'})

    with app.app_context():
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        db.create_all()
        _create_default_admin()

    return app


def _create_default_admin():
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            nickname='Administrator',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
