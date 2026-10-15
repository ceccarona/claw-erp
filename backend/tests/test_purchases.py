def test_list_purchases(client, auth_headers):
    """测试获取采购订单列表"""
    response = client.get('/api/purchases', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_purchase(client, auth_headers, sample_supplier, sample_product):
    """测试创建采购订单"""
    response = client.post('/api/purchases',
        headers=auth_headers,
        json={
            'supplier_id': sample_supplier,
            'order_date': '2024-01-01',
            'remark': '测试采购单',
            'items': [
                {
                    'product_id': sample_product,
                    'quantity': 10,
                    'unit_price': 8.5
                }
            ]
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_no' in data
    assert data['supplier_id'] == sample_supplier


def test_get_purchase(client, auth_headers, sample_supplier, sample_product):
    """测试获取单个采购订单"""
    create_response = client.post('/api/purchases',
        headers=auth_headers,
        json={
            'supplier_id': sample_supplier,
            'order_date': '2024-01-01',
            'items': [{'product_id': sample_product, 'quantity': 5, 'unit_price': 10}]
        }
    )
    purchase_id = create_response.get_json()['id']
    
    response = client.get(f'/api/purchases/{purchase_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == purchase_id
