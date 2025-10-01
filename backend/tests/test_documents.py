import pytest
import io
from models import Document, db

class TestDocuments:
    """文档管理相关测试"""
    
    def test_get_documents_empty(self, client, auth_headers):
        """测试获取空文档列表"""
        response = client.get('/api/documents/', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['documents'] == []
        assert response.json['total'] == 0
    
    def test_upload_txt_file(self, client, auth_headers, app):
        """测试上传TXT文件"""
        data = {
            'file': (io.BytesIO(b"This is a test document content."), 'test.txt'),
            'category': 'test'
        }
        
        response = client.post(
            '/api/documents/upload',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        assert 'document' in response.json
        assert response.json['document']['title'] == 'test'
        assert response.json['document']['source'] == '手动上传'
    
    def test_upload_unsupported_file(self, client, auth_headers):
        """测试上传不支持的文件类型"""
        data = {
            'file': (io.BytesIO(b"data"), 'test.exe')
        }
        
        response = client.post(
            '/api/documents/upload',
            data=data,
            headers=auth_headers,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        assert '不支持的文件类型' in response.json['error']
    
    def test_get_document_by_id(self, client, auth_headers, app, test_user):
        """测试获取单个文档"""
        # 创建测试文档
        with app.app_context():
            doc = Document(
                user_id=test_user.id,
                title='Test Document',
                content='Test content',
                summary='Test summary',
                source='test',
                category='test'
            )
            db.session.add(doc)
            db.session.commit()
            doc_id = doc.id
        
        response = client.get(f'/api/documents/{doc_id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'document' in response.json
        assert response.json['document']['title'] == 'Test Document'
        assert 'content' in response.json['document']
    
    def test_get_nonexistent_document(self, client, auth_headers):
        """测试获取不存在的文档"""
        response = client.get('/api/documents/9999', headers=auth_headers)
        
        assert response.status_code == 404
        assert '文档不存在' in response.json['error']
    
    def test_update_document(self, client, auth_headers, app, test_user):
        """测试更新文档"""
        # 创建测试文档
        with app.app_context():
            doc = Document(
                user_id=test_user.id,
                title='Original Title',
                content='Original content',
                source='test'
            )
            db.session.add(doc)
            db.session.commit()
            doc_id = doc.id
        
        # 更新文档
        response = client.put(
            f'/api/documents/{doc_id}',
            headers=auth_headers,
            json={
                'title': 'Updated Title',
                'category': 'updated',
                'tags': ['tag1', 'tag2']
            }
        )
        
        assert response.status_code == 200
        assert response.json['document']['title'] == 'Updated Title'
        assert response.json['document']['category'] == 'updated'
        assert 'tag1' in response.json['document']['tags']
    
    def test_delete_document(self, client, auth_headers, app, test_user):
        """测试删除文档"""
        # 创建测试文档
        with app.app_context():
            doc = Document(
                user_id=test_user.id,
                title='To Delete',
                content='Content',
                source='test'
            )
            db.session.add(doc)
            db.session.commit()
            doc_id = doc.id
        
        # 删除文档
        response = client.delete(f'/api/documents/{doc_id}', headers=auth_headers)
        
        assert response.status_code == 200
        assert '删除成功' in response.json['message']
    
    def test_batch_delete_documents(self, client, auth_headers, app, test_user):
        """测试批量删除文档"""
        # 创建多个测试文档
        doc_ids = []
        with app.app_context():
            for i in range(3):
                doc = Document(
                    user_id=test_user.id,
                    title=f'Doc {i}',
                    content=f'Content {i}',
                    source='test'
                )
                db.session.add(doc)
            db.session.commit()
            
            docs = Document.query.filter_by(user_id=test_user.id).all()
            doc_ids = [d.id for d in docs]
        
        # 批量删除
        response = client.post(
            '/api/documents/batch-delete',
            headers=auth_headers,
            json={'ids': doc_ids}
        )
        
        assert response.status_code == 200
        assert response.json['deleted_count'] == 3
    
    def test_get_categories(self, client, auth_headers, app, test_user):
        """测试获取分类列表"""
        # 创建不同分类的文档
        with app.app_context():
            for category in ['科技', '财经', '体育']:
                doc = Document(
                    user_id=test_user.id,
                    title=f'{category}新闻',
                    content='Content',
                    category=category,
                    source='test'
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.get('/api/documents/categories', headers=auth_headers)
        
        assert response.status_code == 200
        assert '科技' in response.json['categories']
        assert '财经' in response.json['categories']
        assert '体育' in response.json['categories']
    
    def test_filter_documents_by_category(self, client, auth_headers, app, test_user):
        """测试按分类筛选文档"""
        # 创建不同分类的文档
        with app.app_context():
            for i, category in enumerate(['科技', '财经']):
                doc = Document(
                    user_id=test_user.id,
                    title=f'{category}新闻{i}',
                    content='Content',
                    category=category,
                    source='test'
                )
                db.session.add(doc)
            db.session.commit()
        
        # 筛选科技类
        response = client.get('/api/documents/?category=科技', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['total'] == 1
        assert response.json['documents'][0]['category'] == '科技'


