def test_list_inventory(client, auth_headers):
    """测试获取库存列表"""
    response = client.get('/api/inventory', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_get_inventory(client, auth_headers, sample_product):
    """测试获取单个商品库存"""
    response = client.get(f'/api/inventory/{sample_product}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['product_id'] == sample_product


def test_get_low_stock_items(client, auth_headers, app, sample_category, sample_unit):
    """测试获取低库存商品"""
    with app.app_context():
        from models import db, Product, Inventory
        
        low_stock_product = Product(
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
        db.session.add(low_stock_product)
        db.session.flush()
        
        inventory = Inventory(product_id=low_stock_product.id, quantity=10)
        db.session.add(inventory)
        db.session.commit()
    
    response = client.get('/api/inventory/low-stock', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert len(data['items']) > 0


def test_filter_low_stock(client, auth_headers):
    """测试筛选低库存"""
    response = client.get('/api/inventory?low_stock=true', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data


def test_inventory_logs(client, auth_headers):
    """测试获取库存日志"""
    response = client.get('/api/inventory/logs', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
