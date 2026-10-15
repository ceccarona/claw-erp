def test_list_suppliers(client, auth_headers):
    """测试获取供应商列表"""
    response = client.get('/api/suppliers', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_supplier(client, auth_headers):
    """测试创建供应商"""
    response = client.post('/api/suppliers',
        headers=auth_headers,
        json={
            'code': 'S999',
            'name': '新供应商',
            'contact': '王五',
            'phone': '13700137000',
            'address': '供应商地址'
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == '新供应商'


def test_get_supplier(client, auth_headers, sample_supplier):
    """测试获取单个供应商"""
    response = client.get(f'/api/suppliers/{sample_supplier}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_supplier


def test_update_supplier(client, auth_headers, sample_supplier):
    """测试更新供应商"""
    response = client.put(f'/api/suppliers/{sample_supplier}',
        headers=auth_headers,
        json={'name': '更新后的供应商'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '更新后的供应商'


def test_delete_supplier(client, auth_headers, sample_supplier):
    """测试删除供应商"""
    response = client.delete(f'/api/suppliers/{sample_supplier}', headers=auth_headers)
    assert response.status_code == 200
