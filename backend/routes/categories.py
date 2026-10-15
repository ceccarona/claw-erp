from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Category

bp = Blueprint('categories', __name__)


def serialize_category(c, max_depth=10, current_depth=0):
    if current_depth > max_depth:
        return {'id': c.id, 'name': c.name, 'parent_id': c.parent_id, 'children': []}
    return {
        'id': c.id,
        'name': c.name,
        'parent_id': c.parent_id,
        'children': [serialize_category(child, max_depth, current_depth + 1) for child in c.children] if c.children else []
    }


def get_all_descendant_ids(category_id):
    """获取分类的所有后代ID"""
    descendants = set()
    to_check = [category_id]
    
    while to_check:
        current_id = to_check.pop()
        children = Category.query.filter_by(parent_id=current_id).all()
        for child in children:
            if child.id not in descendants:
                descendants.add(child.id)
                to_check.append(child.id)
    
    return descendants


def would_create_cycle(category_id, new_parent_id):
    """检查设置新父分类是否会造成循环"""
    if new_parent_id is None:
        return False
    if category_id == new_parent_id:
        return True
    
    descendants = get_all_descendant_ids(category_id)
    return new_parent_id in descendants


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
    categories = Category.query.filter_by(parent_id=None).order_by(Category.id).all()
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
    parent_id = data.get('parent_id')
    
    if parent_id is not None:
        parent = Category.query.get(parent_id)
        if not parent:
            return jsonify({'error': 'Parent category not found'}), 404
    
    category = Category(
        name=data.get('name'),
        parent_id=parent_id
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
        new_parent_id = data['parent_id']
        if would_create_cycle(id, new_parent_id):
            return jsonify({'error': 'Cannot set parent: would create a cycle'}), 400
        category.parent_id = new_parent_id
    
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
