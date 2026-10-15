def test_login_success(client):
    """测试登录成功"""
    response = client.post('/api/auth/login', json={
        'username': 'testadmin',
        'password': 'test123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert 'user' in data


def test_login_invalid_credentials(client):
    """测试登录失败 - 错误密码"""
    response = client.post('/api/auth/login', json={
        'username': 'testadmin',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_login_missing_fields(client):
    """测试登录失败 - 缺少字段"""
    response = client.post('/api/auth/login', json={
        'username': 'testadmin'
    })
    assert response.status_code == 400


def test_get_current_user(client, auth_headers):
    """测试获取当前用户信息"""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['username'] == 'testadmin'


def test_get_current_user_unauthorized(client):
    """测试未授权访问"""
    response = client.get('/api/auth/me')
    assert response.status_code == 401
