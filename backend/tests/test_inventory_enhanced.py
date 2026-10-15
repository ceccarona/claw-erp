"""增强的库存测试，覆盖边界条件和低库存筛选"""


def test_low_stock_filter_true(client, auth_headers, app, sample_category, sample_unit):
    """测试低库存筛选 - 只返回低库存商品"""
    with app.app_context():
        from models import db, Product, Inventory
        
        # 低库存商品
        low_product = Product(
            code='P_LOW',
            name='低库存商品',
            category_id=sample_category,
            unit_id=sample_unit,
            cost_price=10.0,
            sale_price=15.0,
            stock_min=50,
            stock_max=100,
            status=1
        )
        db.session.add(low_product)
        db.session.flush()
        
        low_inv = Inventory(product_id=low_product.id, quantity=10)
        db.session.add(low_inv)
        
        # 正常库存商品
        normal_product = Product(
            code='P_NORMAL',
            name='正常库存商品',
            category_id=sample_category,
            unit_id=sample_unit,
            cost_price=10.0,
            sale_price=15.0,
            stock_min=10,
            stock_max=100,
            status=1
        )
        db.session.add(normal_product)
        db.session.flush()
        
        normal_inv = Inventory(product_id=normal_product.id, quantity=50)
        db.session.add(normal_inv)
        
        db.session.commit()
    
    response = client.get('/api/inventory?low_stock=true', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    
    assert len(data['items']) >= 1
    for item in data['items']:
        assert item['quantity'] < item['stock_min']
        assert item['stock_min'] > 0


def test_low_stock_filter_false(client, auth_headers, app, sample_category, sample_unit):
    """测试正常库存筛选 - 只返回正常库存商品"""
    with app.app_context():
        from models import db, Product, Inventory
        
        # 低库存商品
        low_product = Product(
            code='P_LOW2',
            name='低库存商品2',
            category_id=sample_category,
            unit_id=sample_unit,
            stock_min=50,
            stock_max=100,
            status=1
        )
        db.session.add(low_product)
        db.session.flush()
        
        low_inv = Inventory(product_id=low_product.id, quantity=10)
        db.session.add(low_inv)
        
        # 正常库存商品
        normal_product = Product(
            code='P_NORMAL2',
            name='正常库存商品2',
            category_id=sample_category,
            unit_id=sample_unit,
            stock_min=10,
            stock_max=100,
            status=1
        )
        db.session.add(normal_product)
        db.session.flush()
        
        normal_inv = Inventory(product_id=normal_product.id, quantity=50)
        db.session.add(normal_inv)
        
        db.session.commit()
    
    response = client.get('/api/inventory?low_stock=false', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    
    for item in data['items']:
        # 正常库存：要么 stock_min=0，要么 quantity >= stock_min
        assert item['stock_min'] == 0 or item['quantity'] >= item['stock_min']


def test_boundary_stock_equal_min(client, auth_headers, app, sample_category, sample_unit):
    """测试边界条件：库存等于最低库存应该是正常库存"""
    with app.app_context():
        from models import db, Product, Inventory
        
        product = Product(
            code='P_BOUNDARY',
            name='边界测试商品',
            category_id=sample_category,
            unit_id=sample_unit,
            stock_min=20,
            stock_max=100,
            status=1
        )
        db.session.add(product)
        db.session.flush()
        
        inv = Inventory(product_id=product.id, quantity=20)
        db.session.add(inv)
        db.session.commit()
        product_id = product.id
    
    # 应该在正常库存中
    response = client.get('/api/inventory?low_stock=false', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    found = any(item['product_id'] == product_id for item in data['items'])
    assert found
    
    # 不应该在低库存中
    response = client.get('/api/inventory?low_stock=true', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    found = any(item['product_id'] == product_id for item in data['items'])
    assert not found


def test_stock_min_zero(client, auth_headers, app, sample_category, sample_unit):
    """测试 stock_min=0 的商品不出现在低库存列表"""
    with app.app_context():
        from models import db, Product, Inventory
        
        product = Product(
            code='P_ZERO_MIN',
            name='无最低库存商品',
            category_id=sample_category,
            unit_id=sample_unit,
            stock_min=0,
            stock_max=100,
            status=1
        )
        db.session.add(product)
        db.session.flush()
        
        inv = Inventory(product_id=product.id, quantity=5)
        db.session.add(inv)
        db.session.commit()
        product_id = product.id
    
    response = client.get('/api/inventory/low-stock', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    
    found = any(item['product_id'] == product_id for item in data['items'])
    assert not found


def test_low_stock_no_inventory_record(client, auth_headers, app, sample_category, sample_unit):
    """测试没有库存记录的商品（实际库存为0）出现在低库存列表"""
    with app.app_context():
        from models import db, Product
        
        product = Product(
            code='P_NO_INV',
            name='无库存记录商品',
            category_id=sample_category,
            unit_id=sample_unit,
            stock_min=10,
            stock_max=100,
            status=1
        )
        db.session.add(product)
        db.session.commit()
        product_id = product.id
    
    response = client.get('/api/inventory/low-stock', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    
    found_item = None
    for item in data['items']:
        if item['product_id'] == product_id:
            found_item = item
            break
    
    assert found_item is not None
    assert found_item['quantity'] == 0


def test_purchase_updates_inventory(client, auth_headers, sample_supplier, sample_product, app):
    """测试采购入库更新库存数量"""
    with app.app_context():
        from models import Inventory
        inv = Inventory.query.filter_by(product_id=sample_product).first()
        initial_qty = float(inv.quantity) if inv else 0
    
    # 创建并入库采购订单
    create_response = client.post('/api/purchases',
        headers=auth_headers,
        json={
            'supplier_id': sample_supplier,
            'order_date': '2024-01-01',
            'items': [{'product_id': sample_product, 'quantity': 20, 'unit_price': 10}]
        }
    )
    assert create_response.status_code == 201
    purchase_id = create_response.get_json()['id']
    
    receive_response = client.post(f'/api/purchases/{purchase_id}/receive', headers=auth_headers)
    assert receive_response.status_code == 200
    
    # 验证库存增加
    inv_response = client.get(f'/api/inventory/{sample_product}', headers=auth_headers)
    assert inv_response.status_code == 200
    inv_data = inv_response.get_json()
    assert inv_data['quantity'] == initial_qty + 20


def test_sales_updates_inventory(client, auth_headers, sample_customer, sample_product, app):
    """测试销售出库更新库存数量"""
    with app.app_context():
        from models import Inventory
        inv = Inventory.query.filter_by(product_id=sample_product).first()
        initial_qty = float(inv.quantity) if inv else 0
    
    # 创建并出库销售订单
    create_response = client.post('/api/sales',
        headers=auth_headers,
        json={
            'customer_id': sample_customer,
            'order_date': '2024-01-01',
            'items': [{'product_id': sample_product, 'quantity': 10, 'unit_price': 15}]
        }
    )
    assert create_response.status_code == 201
    sale_id = create_response.get_json()['id']
    
    deliver_response = client.post(f'/api/sales/{sale_id}/deliver', headers=auth_headers)
    assert deliver_response.status_code == 200
    
    # 验证库存减少
    inv_response = client.get(f'/api/inventory/{sample_product}', headers=auth_headers)
    assert inv_response.status_code == 200
    inv_data = inv_response.get_json()
    assert inv_data['quantity'] == initial_qty - 10
