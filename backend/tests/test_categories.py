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
    
    get_response = client.get(f'/api/categories/{sample_category}', headers=auth_headers)
    assert get_response.status_code == 404


def test_delete_category_not_found(client, auth_headers):
    """测试删除不存在的分类"""
    response = client.delete('/api/categories/9999', headers=auth_headers)
    assert response.status_code == 404


def test_delete_category_with_children(client, auth_headers, app):
    """测试删除有子分类的分类应该失败"""
    with app.app_context():
        from models import db, Category
        
        parent = Category(name='父分类')
        db.session.add(parent)
        db.session.flush()
        
        child = Category(name='子分类', parent_id=parent.id)
        db.session.add(child)
        db.session.commit()
        parent_id = parent.id
    
    response = client.delete(f'/api/categories/{parent_id}', headers=auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'children' in data['error']


def test_delete_category_with_products(client, auth_headers, sample_category, sample_unit):
    """测试删除有商品的分类应该失败"""
    with client.application.app_context():
        from models import db, Product
        
        product = Product(
            code='P_TEST',
            name='测试商品',
            category_id=sample_category,
            unit_id=sample_unit,
            cost_price=10.0,
            sale_price=15.0
        )
        db.session.add(product)
        db.session.commit()
    
    response = client.delete(f'/api/categories/{sample_category}', headers=auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'products' in data['error']


def test_category_cycle_prevention(client, auth_headers, app):
    """测试防止分类循环引用"""
    with app.app_context():
        from models import db, Category
        
        cat1 = Category(name='分类1')
        db.session.add(cat1)
        db.session.flush()
        
        cat2 = Category(name='分类2', parent_id=cat1.id)
        db.session.add(cat2)
        db.session.flush()
        
        cat3 = Category(name='分类3', parent_id=cat2.id)
        db.session.add(cat3)
        db.session.commit()
        
        cat1_id = cat1.id
        cat3_id = cat3.id
    
    response = client.put(f'/api/categories/{cat1_id}',
        headers=auth_headers,
        json={'parent_id': cat3_id}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'cycle' in data['error']


def test_category_self_parent(client, auth_headers, sample_category):
    """测试分类不能设置自己为父分类"""
    response = client.put(f'/api/categories/{sample_category}',
        headers=auth_headers,
        json={'parent_id': sample_category}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert 'cycle' in data['error']
