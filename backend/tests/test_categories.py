def test_list_categories(client, auth_headers):
    """测试获取分类列表"""
    response = client.get('/api/categories', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'items' in data
    assert 'total' in data


def test_create_category(client, auth_headers):
    """测试创建分类"""
    response = client.post('/api/categories', 
        headers=auth_headers,
        json={'name': '电子产品'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == '电子产品'


def test_get_category(client, auth_headers, sample_category):
    """测试获取单个分类"""
    response = client.get(f'/api/categories/{sample_category}', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == sample_category


def test_update_category(client, auth_headers, sample_category):
    """测试更新分类"""
    response = client.put(f'/api/categories/{sample_category}',
        headers=auth_headers,
        json={'name': '更新后的分类'}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == '更新后的分类'


def test_delete_category(client, auth_headers, sample_category):
    """测试删除分类"""
    response = client.delete(f'/api/categories/{sample_category}', headers=auth_headers)
    assert response.status_code == 200


def test_delete_category_not_found(client, auth_headers):
    """测试删除不存在的分类"""
    response = client.delete('/api/categories/9999', headers=auth_headers)
    assert response.status_code == 404
