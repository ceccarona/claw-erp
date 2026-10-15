def test_list_customers(client, auth_headers):
    """测试获取客户列表"""
    response = client.get('/api/customers', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_customer(client, auth_headers):
    """测试创建客户"""
    response = client.post('/api/customers',
        headers=auth_headers,
        json={
            'code': 'C999',
            'name': '新客户',
            'contact': '赵六',
            'phone': '13600136000',
            'address': '客户地址',
            'credit_limit': 5000
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == '新客户'


def test_get_customer(client, auth_headers, sample_customer):
    """测试获取单个客户"""
    response = client.get(f'/api/customers/{sample_customer}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_customer


def test_update_customer(client, auth_headers, sample_customer):
    """测试更新客户"""
    response = client.put(f'/api/customers/{sample_customer}',
        headers=auth_headers,
        json={'name': '更新后的客户'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '更新后的客户'


def test_delete_customer(client, auth_headers, sample_customer):
    """测试删除客户"""
    response = client.delete(f'/api/customers/{sample_customer}', headers=auth_headers)
    assert response.status_code == 200
