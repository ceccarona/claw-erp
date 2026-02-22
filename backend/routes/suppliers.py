from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Supplier

bp = Blueprint('suppliers', __name__)


def serialize_supplier(s):
    return {
        'id': s.id,
        'code': s.code,
        'name': s.name,
        'contact': s.contact,
        'phone': s.phone,
        'address': s.address,
        'status': s.status,
        'created_at': s.created_at.isoformat() if s.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', type=int)
    
    query = Supplier.query
    if search:
        query = query.filter(db.or_(
            Supplier.name.like(f'%{search}%'),
            Supplier.code.like(f'%{search}%')
        ))
    if status is not None:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(Supplier.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_supplier(s) for s in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    return jsonify(serialize_supplier(supplier))


@bp.route('', methods=['POST'])
@jwt_required()
def create_supplier():
    data = request.get_json()
    
    if Supplier.query.filter_by(code=data.get('code')).first():
        return jsonify({'error': 'Supplier code already exists'}), 400
    
    supplier = Supplier(
        code=data.get('code'),
        name=data.get('name'),
        contact=data.get('contact'),
        phone=data.get('phone'),
        address=data.get('address'),
        status=data.get('status', 1)
    )
    db.session.add(supplier)
    db.session.commit()
    
    return jsonify(serialize_supplier(supplier)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('code') and data['code'] != supplier.code:
        if Supplier.query.filter_by(code=data['code']).first():
            return jsonify({'error': 'Supplier code already exists'}), 400
        supplier.code = data['code']
    
    if data.get('name'):
        supplier.name = data['name']
    if 'contact' in data:
        supplier.contact = data['contact']
    if 'phone' in data:
        supplier.phone = data['phone']
    if 'address' in data:
        supplier.address = data['address']
    if 'status' in data:
        supplier.status = data['status']
    
    db.session.commit()
    return jsonify(serialize_supplier(supplier))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({'message': 'Supplier deleted successfully'})
