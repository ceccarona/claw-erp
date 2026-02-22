from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, PurchaseOrder, PurchaseOrderItem, Inventory, InventoryLog, Product
from datetime import datetime
import uuid

bp = Blueprint('purchases', __name__)


def serialize_order(o):
    return {
        'id': o.id,
        'order_no': o.order_no,
        'supplier_id': o.supplier_id,
        'supplier_name': o.supplier.name if o.supplier else None,
        'order_date': o.order_date.isoformat() if o.order_date else None,
        'total_amount': float(o.total_amount) if o.total_amount else 0,
        'status': o.status,
        'remark': o.remark,
        'created_by': o.created_by,
        'created_at': o.created_at.isoformat() if o.created_at else None,
        'items': [serialize_item(i) for i in o.items]
    }


def serialize_item(i):
    return {
        'id': i.id,
        'product_id': i.product_id,
        'product_name': i.product.name if i.product else None,
        'product_code': i.product.code if i.product else None,
        'quantity': float(i.quantity) if i.quantity else 0,
        'unit_price': float(i.unit_price) if i.unit_price else 0,
        'amount': float(i.amount) if i.amount else 0
    }


@bp.route('', methods=['GET'])
@jwt_required()
def list_purchases():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    supplier_id = request.args.get('supplier_id', type=int)
    
    query = PurchaseOrder.query
    if status:
        query = query.filter_by(status=status)
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    pagination = query.order_by(PurchaseOrder.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_order(o) for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_purchase(id):
    order = PurchaseOrder.query.get_or_404(id)
    return jsonify(serialize_order(order))


@bp.route('', methods=['POST'])
@jwt_required()
def create_purchase():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    order_no = f"PO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    
    order = PurchaseOrder(
        order_no=order_no,
        supplier_id=data.get('supplier_id'),
        order_date=datetime.strptime(data.get('order_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date() if data.get('order_date') else datetime.now().date(),
        total_amount=0,
        status='draft',
        remark=data.get('remark'),
        created_by=user_id
    )
    db.session.add(order)
    db.session.flush()
    
    total_amount = 0
    for item_data in data.get('items', []):
        quantity = float(item_data.get('quantity', 0))
        unit_price = float(item_data.get('unit_price', 0))
        amount = quantity * unit_price
        
        item = PurchaseOrderItem(
            order_id=order.id,
            product_id=item_data.get('product_id'),
            quantity=quantity,
            unit_price=unit_price,
            amount=amount
        )
        db.session.add(item)
        total_amount += amount
    
    order.total_amount = total_amount
    db.session.commit()
    
    return jsonify(serialize_order(order)), 201


@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_purchase(id):
    order = PurchaseOrder.query.get_or_404(id)
    if order.status != 'draft':
        return jsonify({'error': 'Only draft orders can be updated'}), 400
    
    data = request.get_json()
    
    if 'supplier_id' in data:
        order.supplier_id = data['supplier_id']
    if 'order_date' in data:
        order.order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
    if 'remark' in data:
        order.remark = data['remark']
    
    if 'items' in data:
        PurchaseOrderItem.query.filter_by(order_id=order.id).delete()
        total_amount = 0
        for item_data in data['items']:
            quantity = float(item_data.get('quantity', 0))
            unit_price = float(item_data.get('unit_price', 0))
            amount = quantity * unit_price
            
            item = PurchaseOrderItem(
                order_id=order.id,
                product_id=item_data.get('product_id'),
                quantity=quantity,
                unit_price=unit_price,
                amount=amount
            )
            db.session.add(item)
            total_amount += amount
        order.total_amount = total_amount
    
    db.session.commit()
    return jsonify(serialize_order(order))


@bp.route('/<int:id>/receive', methods=['POST'])
@jwt_required()
def receive_purchase(id):
    user_id = get_jwt_identity()
    order = PurchaseOrder.query.get_or_404(id)
    
    if order.status == 'received':
        return jsonify({'error': 'Order already received'}), 400
    
    if order.status == 'cancelled':
        return jsonify({'error': 'Cancelled order cannot be received'}), 400
    
    for item in order.items:
        product = Product.query.get(item.product_id)
        if not product:
            continue
        
        inventory = Inventory.query.filter_by(product_id=item.product_id).first()
        if not inventory:
            inventory = Inventory(product_id=item.product_id, quantity=0)
            db.session.add(inventory)
        
        inventory.quantity += item.quantity
        
        log = InventoryLog(
            product_id=item.product_id,
            change_type='purchase_in',
            quantity=item.quantity,
            order_no=order.order_no
        )
        db.session.add(log)
    
    order.status = 'received'
    db.session.commit()
    
    return jsonify(serialize_order(order))


@bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_purchase(id):
    order = PurchaseOrder.query.get_or_404(id)
    
    if order.status == 'received':
        return jsonify({'error': 'Received order cannot be cancelled'}), 400
    
    if order.status == 'cancelled':
        return jsonify({'error': 'Order already cancelled'}), 400
    
    order.status = 'cancelled'
    db.session.commit()
    
    return jsonify(serialize_order(order))
