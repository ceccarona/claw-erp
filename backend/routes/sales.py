from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, SalesOrder, SalesOrderItem, Inventory, InventoryLog, Product
from datetime import datetime
import uuid

bp = Blueprint('sales', __name__)


def serialize_order(o):
    return {
        'id': o.id,
        'order_no': o.order_no,
        'customer_id': o.customer_id,
        'customer_name': o.customer.name if o.customer else None,
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
def list_sales():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status', '')
    customer_id = request.args.get('customer_id', type=int)
    
    query = SalesOrder.query
    if status:
        query = query.filter_by(status=status)
    if customer_id:
        query = query.filter_by(customer_id=customer_id)
    
    pagination = query.order_by(SalesOrder.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [serialize_order(o) for o in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page
    })


@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_sale(id):
    order = SalesOrder.query.get_or_404(id)
    return jsonify(serialize_order(order))


@bp.route('', methods=['POST'])
@jwt_required()
def create_sale():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    order_no = f"SO{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    
    order = SalesOrder(
        order_no=order_no,
        customer_id=data.get('customer_id'),
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
        
        item = SalesOrderItem(
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
def update_sale(id):
    order = SalesOrder.query.get_or_404(id)
    if order.status != 'draft':
        return jsonify({'error': 'Only draft orders can be updated'}), 400
    
    data = request.get_json()
    
    if 'customer_id' in data:
        order.customer_id = data['customer_id']
    if 'order_date' in data:
        order.order_date = datetime.strptime(data['order_date'], '%Y-%m-%d').date()
    if 'remark' in data:
        order.remark = data['remark']
    
    if 'items' in data:
        SalesOrderItem.query.filter_by(order_id=order.id).delete()
        total_amount = 0
        for item_data in data['items']:
            quantity = float(item_data.get('quantity', 0))
            unit_price = float(item_data.get('unit_price', 0))
            amount = quantity * unit_price
            
            item = SalesOrderItem(
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


@bp.route('/<int:id>/deliver', methods=['POST'])
@jwt_required()
def deliver_sale(id):
    user_id = get_jwt_identity()
    order = SalesOrder.query.get_or_404(id)
    
    if order.status == 'delivered':
        return jsonify({'error': 'Order already delivered'}), 400
    
    if order.status == 'cancelled':
        return jsonify({'error': 'Cancelled order cannot be delivered'}), 400
    
    for item in order.items:
        product = Product.query.get(item.product_id)
        if not product:
            continue
        
        inventory = Inventory.query.filter_by(product_id=item.product_id).first()
        if not inventory or inventory.quantity < item.quantity:
            return jsonify({'error': f'Insufficient inventory for product {product.name}'}), 400
        
        inventory.quantity -= item.quantity
        
        log = InventoryLog(
            product_id=item.product_id,
            change_type='sales_out',
            quantity=-item.quantity,
            order_no=order.order_no
        )
        db.session.add(log)
    
    order.status = 'delivered'
    db.session.commit()
    
    return jsonify(serialize_order(order))


@bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_sale(id):
    order = SalesOrder.query.get_or_404(id)
    
    if order.status == 'delivered':
        return jsonify({'error': 'Delivered order cannot be cancelled'}), 400
    
    if order.status == 'cancelled':
        return jsonify({'error': 'Order already cancelled'}), 400
    
    order.status = 'cancelled'
    db.session.commit()
    
    return jsonify(serialize_order(order))
