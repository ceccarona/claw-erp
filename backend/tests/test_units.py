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


def test_search_units(client, auth_headers, sample_unit):
    """测试搜索单位"""
    response = client.get('/api/units?search=个', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['items']) > 0
