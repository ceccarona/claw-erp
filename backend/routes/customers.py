from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Customer

bp = Blueprint('customers', __name__)


def serialize_customer(c):
    return {
        'id': c.id,
        'code': c.code,
        'name': c.name,
        'contact': c.contact,
        'phone': c.phone,
        'address': c.address,
        'credit_limit': float(c.credit_limit) if c.credit_limit else 0,
        'status': c.status,
        'created_at': c.created_at.isoformat() if c.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_customers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', type=int)
    
    query = Customer.query
    if search:
        query = query.filter(db.or_(
            Customer.name.like(f'%{search}%'),
            Customer.code.like(f'%{search}%')
        ))
    if status is not None:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Customer.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_customer(c) for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify(serialize_customer(customer))


@bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    data = request.get_json()
    
    if Customer.query.filter_by(code=data.get('code')).first():
        return jsonify({'error': 'Customer code already exists'}), 400
    
    customer = Customer(
        code=data.get('code'),
        name=data.get('name'),
        contact=data.get('contact'),
        phone=data.get('phone'),
        address=data.get('address'),
        credit_limit=data.get('credit_limit', 0),
        status=data.get('status', 1)
    )
    db.session.add(customer)
    db.session.commit()
    
    return jsonify(serialize_customer(customer)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('code') and data['code'] != customer.code:
        if Customer.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Customer code already exists'}), 400
        customer.code = data['code']
    
    if data.get('name'):
        customer.name = data['name']
    if 'contact' in data:
        customer.contact = data['contact']
    if 'phone' in data:
        customer.phone = data['phone']
    if 'address' in data:
        customer.address = data['address']
    if 'credit_limit' in data:
        customer.credit_limit = data['credit_limit']
    if 'status' in data:
        customer.status = data['status']
    
    db.session.commit()
    return jsonify(serialize_customer(customer))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted successfully'})
