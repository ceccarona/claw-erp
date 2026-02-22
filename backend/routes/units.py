from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Unit

bp = Blueprint('units', __name__)


def serialize_unit(u):
    return {
        'id': u.id,
        'name': u.name
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_units():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Unit.query
    if search:
        query = query.filter(Unit.name.like(f'%{search}%'))
    
    pagination = query.order_by(Unit.id).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_unit(u) for u in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/all', methods=['GET'])
@jwt_required()
def list_all_units():
    units = Unit.query.order_by(Unit.id).all()
    return jsonify([serialize_unit(u) for u in units])


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_unit(id):
    unit = Unit.query.get_or_404(id)
    return jsonify(serialize_unit(unit))


@bp.route('', methods=['POST'])
@jwt_required()
def create_unit():
    data = request.get_json()
    
    unit = Unit(name=data.get('name'))
    db.session.add(unit)
    db.session.commit()
    
    return jsonify(serialize_unit(unit)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_unit(id):
    unit = Unit.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('name'):
        unit.name = data['name']
    
    db.session.commit()
    return jsonify(serialize_unit(unit))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_unit(id):
    unit = Unit.query.get_or_404(id)
    
    if unit.products.count() > 0:
        return jsonify({'error': 'Cannot delete unit with products'}), 400
    
    db.session.delete(unit)
    db.session.commit()
    return jsonify({'message': 'Unit deleted successfully'})
