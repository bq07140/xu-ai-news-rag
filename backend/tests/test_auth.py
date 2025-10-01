import pytest
from models import User, db

class TestAuth:
    """认证相关测试"""
    
    def test_register_success(self, client):
        """测试注册成功"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        assert 'user' in response.json
        assert response.json['user']['username'] == 'newuser'
    
    def test_register_missing_fields(self, client):
        """测试注册缺少字段"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_register_duplicate_username(self, client, test_user):
        """测试注册重复用户名"""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 409
        assert '用户名已存在' in response.json['error']
    
    def test_register_short_password(self, client):
        """测试注册密码过短"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': '123'
        })
        
        assert response.status_code == 400
        assert '密码长度' in response.json['error']
    
    def test_login_success(self, client, test_user):
        """测试登录成功"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'testpassword123'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'refresh_token' in response.json
        assert 'user' in response.json
    
    def test_login_wrong_password(self, client, test_user):
        """测试登录密码错误"""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        assert '用户名或密码错误' in response.json['error']
    
    def test_login_nonexistent_user(self, client):
        """测试登录不存在的用户"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """测试获取当前用户信息"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'user' in response.json
        assert response.json['user']['username'] == 'testuser'
    
    def test_get_current_user_without_token(self, client):
        """测试未登录获取用户信息"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_logout(self, client, auth_headers):
        """测试登出"""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        assert '登出成功' in response.json['message']


