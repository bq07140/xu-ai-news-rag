import pytest
from models import Document, db

class TestSearch:
    """搜索功能相关测试"""
    
    def test_semantic_search_empty_index(self, client, auth_headers):
        """测试空索引的语义搜索"""
        response = client.post(
            '/api/search/semantic',
            headers=auth_headers,
            json={'query': '人工智能'}
        )
        
        assert response.status_code == 200
        assert response.json['count'] == 0
        assert response.json['trigger_web_search'] == True
    
    def test_semantic_search_with_documents(self, client, auth_headers, app, test_user):
        """测试有文档时的语义搜索"""
        # 创建测试文档并添加到向量库
        with app.app_context():
            doc = Document(
                user_id=test_user.id,
                title='人工智能最新进展',
                content='人工智能技术在各个领域都取得了重大突破，深度学习、自然语言处理等技术日益成熟。',
                source='test',
                category='科技'
            )
            db.session.add(doc)
            db.session.commit()
            
            # 添加到向量库
            vector_store = app.config['VECTOR_STORE']
            text = f"{doc.title} {doc.content}"
            vector_store.add_document(doc.id, text)
            doc.vector_id = doc.id
            db.session.commit()
        
        # 执行搜索
        response = client.post(
            '/api/search/semantic',
            headers=auth_headers,
            json={'query': '人工智能发展'}
        )
        
        assert response.status_code == 200
        assert response.json['count'] >= 0
        assert 'results' in response.json
    
    def test_web_search(self, client, auth_headers):
        """测试联网搜索"""
        response = client.post(
            '/api/search/web',
            headers=auth_headers,
            json={'query': '量子计算最新进展', 'num_results': 3}
        )
        
        assert response.status_code == 200
        assert 'results' in response.json
        assert 'summary' in response.json
        assert len(response.json['results']) <= 3
    
    def test_combined_search(self, client, auth_headers):
        """测试组合搜索"""
        response = client.post(
            '/api/search/combined',
            headers=auth_headers,
            json={'query': '最新科技新闻'}
        )
        
        assert response.status_code == 200
        assert 'knowledge_base_results' in response.json
        assert 'web_search_triggered' in response.json
    
    def test_get_search_history(self, client, auth_headers):
        """测试获取搜索历史"""
        # 先执行一次搜索
        client.post(
            '/api/search/semantic',
            headers=auth_headers,
            json={'query': '测试查询'}
        )
        
        # 获取历史
        response = client.get('/api/search/history', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'history' in response.json
        assert len(response.json['history']) > 0
    
    def test_search_without_query(self, client, auth_headers):
        """测试缺少查询内容"""
        response = client.post(
            '/api/search/semantic',
            headers=auth_headers,
            json={}
        )
        
        assert response.status_code == 400
        assert '缺少查询内容' in response.json['error']


