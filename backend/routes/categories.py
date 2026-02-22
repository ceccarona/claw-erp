from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Category

bp = Blueprint('categories', __name__)


def serialize_category(c):
    return {
        'id': c.id,
        'name': c.name,
        'parent_id': c.parent_id,
        'children': [serialize_category(child) for child in c.children] if c.children else []
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_categories():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    
    query = Category.query.filter_by(parent_id=None)
    pagination = query.order_by(Category.id).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_category(c) for c in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/all', methods=['GET'])
@jwt_required()
def list_all_categories():
    categories = Category.query.order_by(Category.id).all()
    return jsonify([serialize_category(c) for c in categories])


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_category(id):
    category = Category.query.get_or_404(id)
    return jsonify(serialize_category(category))


@bp.route('', methods=['POST'])
@jwt_required()
def create_category():
    data = request.get_json()
    
    category = Category(
        name=data.get('name'),
        parent_id=data.get('parent_id')
    )
    db.session.add(category)
    db.session.commit()
    
    return jsonify(serialize_category(category)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    category = Category.query.get_or_404(id)
    data = request.get_json()
    
    if data.get('name'):
        category.name = data['name']
    if 'parent_id' in data:
        category.parent_id = data['parent_id']
    
    db.session.commit()
    return jsonify(serialize_category(category))


@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    if category.children.count() > 0:
        return jsonify({'error': 'Cannot delete category with children'}), 400
    
    if category.products.count() > 0:
        return jsonify({'error': 'Cannot delete category with products'}), 400
    
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'})
