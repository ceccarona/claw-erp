def test_list_products(client, auth_headers):
    """测试获取商品列表"""
    response = client.get('/api/products', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_product(client, auth_headers, sample_category, sample_unit):
    """测试创建商品"""
    response = client.post('/api/products',
        headers=auth_headers,
        json={
            'code': 'P999',
            'name': '新商品',
            'category_id': sample_category,
            'unit_id': sample_unit,
            'cost_price': 20.0,
            'sale_price': 30.0,
            'stock_min': 5,
            'stock_max': 50
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == '新商品'


def test_get_product(client, auth_headers, sample_product):
    """测试获取单个商品"""
    response = client.get(f'/api/products/{sample_product}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_product


def test_update_product(client, auth_headers, sample_product):
    """测试更新商品"""
    response = client.put(f'/api/products/{sample_product}',
        headers=auth_headers,
        json={'name': '更新后的商品'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '更新后的商品'


def test_delete_product(client, auth_headers, sample_product):
    """测试删除商品"""
    response = client.delete(f'/api/products/{sample_product}', headers=auth_headers)
    assert response.status_code == 200
