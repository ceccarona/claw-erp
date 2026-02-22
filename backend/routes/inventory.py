from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Inventory, InventoryLog, Product
from datetime import datetime

bp = Blueprint('inventory', __name__)


def serialize_inventory(i):
    return {
        'id': i.id,
        'product_id': i.product_id,
        'product_name': i.product.name if i.product else None,
        'product_code': i.product.code if i.product else None,
        'quantity': float(i.quantity) if i.quantity else 0,
        'stock_min': i.product.stock_min if i.product else 0,
        'stock_max': i.product.stock_max if i.product else 0,
        'updated_at': i.updated_at.isoformat() if i.updated_at else None
    }


def serialize_log(l):
    return {
        'id': l.id,
        'product_id': l.product_id,
        'product_name': l.product.name if l.product else None,
        'change_type': l.change_type,
        'quantity': float(l.quantity) if l.quantity else 0,
        'order_no': l.order_no,
        'created_at': l.created_at.isoformat() if l.created_at else None
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_inventory():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    low_stock = request.args.get('low_stock', type=bool)
    
    query = Inventory.query.join(Product)
    
    if search:
        query = query.filter(db.or_(
            Product.name.like(f'%{search}%'),
            Product.code.like(f'%{search}%')
        ))
    
    if low_stock:
        query = query.filter(Product.stock_min > 0, Inventory.quantity < Product.stock_min)
    
    pagination = query.order_by(Inventory.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_inventory(i) for i in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/<int:product_id>', methods=['GET'])
@jwt_required()
def get_inventory(product_id):
    inventory = Inventory.query.filter_by(product_id=product_id).first()
    if not inventory:
        inventory = Inventory(product_id=product_id, quantity=0)
        db.session.add(inventory)
        db.session.commit()
    return jsonify(serialize_inventory(inventory))


@bp.route('/logs', methods=['GET'])
@jwt_required()
def list_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    product_id = request.args.get('product_id', type=int)
    change_type = request.args.get('change_type', '')
    
    query = InventoryLog.query
    
    if product_id:
        query = query.filter_by(product_id=product_id)
    if change_type:
        query = query.filter_by(change_type=change_type)
    
    pagination = query.order_by(InventoryLog.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_log(l) for l in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/check', methods=['POST'])
@jwt_required()
def check_inventory():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    results = []
    for item_data in data.get('items', []):
        product_id = item_data.get('product_id')
        actual_quantity = float(item_data.get('quantity', 0))
        
        inventory = Inventory.query.filter_by(product_id=product_id).first()
        if not inventory:
            inventory = Inventory(product_id=product_id, quantity=0)
            db.session.add(inventory)
        
        difference = actual_quantity - (inventory.quantity if inventory.quantity else 0)
        
        if difference != 0:
            log = InventoryLog(
                product_id=product_id,
                change_type='check',
                quantity=difference,
                order_no=f'CHECK{datetime.now().strftime("%Y%m%d%H%M%S")}'
            )
            db.session.add(log)
        
        inventory.quantity = actual_quantity
        results.append({
            'product_id': product_id,
            'before': float(inventory.quantity) if inventory.quantity else 0,
            'after': actual_quantity,
            'difference': difference
        })
    
    db.session.commit()
    
    return jsonify({
        'message': 'Inventory check completed',
        'results': results
    })
