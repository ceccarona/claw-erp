from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Product, Category, Unit, Inventory
from datetime import datetime

bp = Blueprint('products', __name__)


def serialize_product(p):
    return {
        'id': p.id,
        'code': p.code,
        'name': p.name,
        'category_id': p.category_id,
        'category_name': p.category.name if p.category else None,
        'unit_id': p.unit_id,
        'unit_name': p.unit.name if p.unit else None,
        'cost_price': float(p.cost_price) if p.cost_price else 0,
        'sale_price': float(p.sale_price) if p.sale_price else 0,
        'stock_min': p.stock_min,
        'stock_max': p.stock_max,
        'status': p.status,
        'quantity': float(p.inventory.quantity) if p.inventory else 0,
        'created_at': p.created_at.isoformat() if p.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', type=int)
    
    query = Product.query
    if search:
        query = query.filter(db.or_(
            Product.name.like(f'%{search}%'),
            Product.code.like(f'%{search}%')
        ))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status is not None:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Product.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_product(p) for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(serialize_product(product))


@bp.route('', methods=['POST'])
@jwt_required()
def create_product():
    data = request.get_json()
    
    if Product.query.filter_by(code=data.get('code')).first():
        return jsonify({'error': 'Product code already exists'}), 400
    
    product = Product(
        code=data.get('code'),
        name=data.get('name'),
        category_id=data.get('category_id'),
        unit_id=data.get('unit_id'),
        cost_price=data.get('cost_price', 0),
        sale_price=data.get('sale_price', 0),
        stock_min=data.get('stock_min', 0),
        stock_max=data.get('stock_max', 0),
        status=data.get('status', 1)
    )
    db.session.add(product)
    db.session.commit()
    
    return jsonify(serialize_product(product)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('code') and data['code'] != product.code:
        if Product.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Product code already exists'}), 400
        product.code = data['code']
    
    if data.get('name'):
        product.name = data['name']
    if 'category_id' in data:
        product.category_id = data['category_id']
    if 'unit_id' in data:
        product.unit_id = data['unit_id']
    if 'cost_price' in data:
        product.cost_price = data['cost_price']
    if 'sale_price' in data:
        product.sale_price = data['sale_price']
    if 'stock_min' in data:
        product.stock_min = data['stock_min']
    if 'stock_max' in data:
        product.stock_max = data['stock_max']
    if 'status' in data:
        product.status = data['status']
    
    db.session.commit()
    return jsonify(serialize_product(product))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
