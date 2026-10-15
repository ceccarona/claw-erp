import pytest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, Category, Unit, Product, Supplier, Customer, Inventory
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def app():
    """创建测试应用"""
    test_db_path = '/tmp/test_claw_erp.db'
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_path}'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.app_context():
        db.create_all()
        
        admin = User(
            username='testadmin',
            password_hash=generate_password_hash('test123'),
            nickname='Test Admin',
            role='admin'
        )
        db.session.add(admin)
        
        user = User(
            username='testuser',
            password_hash=generate_password_hash('test123'),
            nickname='Test User',
            role='user'
        )
        db.session.add(user)
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()
    
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def auth_headers(client):
    """获取认证头"""
    response = client.post('/api/auth/login', json={
        'username': 'testadmin',
        'password': 'test123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def sample_category(app):
    """创建示例分类"""
    with app.app_context():
        category = Category(name='测试分类')
        db.session.add(category)
        db.session.commit()
        return category.id


@pytest.fixture(scope='function')
def sample_unit(app):
    """创建示例单位"""
    with app.app_context():
        unit = Unit(name='个')
        db.session.add(unit)
        db.session.commit()
        return unit.id


@pytest.fixture(scope='function')
def sample_product(app, sample_category, sample_unit):
    """创建示例商品"""
    with app.app_context():
        product = Product(
            code='P001',
            name='测试商品',
            category_id=sample_category,
            unit_id=sample_unit,
            cost_price=10.0,
            sale_price=15.0,
            stock_min=10,
            stock_max=100,
            status=1
        )
        db.session.add(product)
        
        inventory = Inventory(product_id=product.id, quantity=50)
        db.session.add(inventory)
        
        db.session.commit()
        return product.id


@pytest.fixture(scope='function')
def sample_supplier(app):
    """创建示例供应商"""
    with app.app_context():
        supplier = Supplier(
            code='S001',
            name='测试供应商',
            contact='张三',
            phone='13800138000',
            address='测试地址',
            status=1
        )
        db.session.add(supplier)
        db.session.commit()
        return supplier.id


@pytest.fixture(scope='function')
def sample_customer(app):
    """创建示例客户"""
    with app.app_context():
        customer = Customer(
            code='C001',
            name='测试客户',
            contact='李四',
            phone='13900139000',
            address='客户地址',
            credit_limit=10000,
            status=1
        )
        db.session.add(customer)
        db.session.commit()
        return customer.id
