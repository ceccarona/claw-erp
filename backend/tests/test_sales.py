def test_list_sales(client, auth_headers):
    """测试获取销售订单列表"""
    response = client.get('/api/sales', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_sale(client, auth_headers, sample_customer, sample_product):
    """测试创建销售订单"""
    response = client.post('/api/sales',
        headers=auth_headers,
        json={
            'customer_id': sample_customer,
            'order_date': '2024-01-01',
            'remark': '测试销售单',
            'items': [
                {
                    'product_id': sample_product,
                    'quantity': 5,
                    'unit_price': 15.0
                }
            ]
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_no' in data
    assert data['customer_id'] == sample_customer


def test_get_sale(client, auth_headers, sample_customer, sample_product):
    """测试获取单个销售订单"""
    create_response = client.post('/api/sales',
        headers=auth_headers,
        json={
            'customer_id': sample_customer,
            'order_date': '2024-01-01',
            'items': [{'product_id': sample_product, 'quantity': 3, 'unit_price': 20}]
        }
    )
    sale_id = create_response.get_json()['id']
    
    response = client.get(f'/api/sales/{sale_id}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sale_id
