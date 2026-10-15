def test_list_units(client, auth_headers):
    """测试获取单位列表"""
    response = client.get('/api/units', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_unit(client, auth_headers):
    """测试创建单位"""
    response = client.post('/api/units',
        headers=auth_headers,
        json={'name': '件'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == '件'


def test_get_unit(client, auth_headers, sample_unit):
    """测试获取单个单位"""
    response = client.get(f'/api/units/{sample_unit}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_unit


def test_update_unit(client, auth_headers, sample_unit):
    """测试更新单位"""
    response = client.put(f'/api/units/{sample_unit}',
        headers=auth_headers,
        json={'name': '箱'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '箱'


def test_delete_unit(client, auth_headers, sample_unit):
    """测试删除单位"""
    response = client.delete(f'/api/units/{sample_unit}', headers=auth_headers)
    assert response.status_code == 200
    
    get_response = client.get(f'/api/units/{sample_unit}', headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_unit_with_products(client, auth_headers, sample_unit, sample_category):
    """测试删除被商品使用的单位应该失败"""
    with client.application.app_context():
        from models import db, Product
        
        product = Product(
            code='P_UNIT_TEST',
            name='单位测试商品',
            category_id=sample_category,
            unit_id=sample_unit,
            cost_price=10.0,
            sale_price=15.0
        )
        db.session.add(product)
        db.session.commit()
    
    response = client.delete(f'/api/units/{sample_unit}', headers=auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'products' in data['error']


def test_search_units(client, auth_headers, sample_unit):
    """测试搜索单位"""
    response = client.get('/api/units?search=个', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) > 0
