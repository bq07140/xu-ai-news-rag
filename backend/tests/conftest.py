import pytest
import os
import sys

# 添加backend目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建测试CLI运行器"""
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpassword123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def auth_headers(client, test_user):
    """获取认证头"""
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpassword123'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


