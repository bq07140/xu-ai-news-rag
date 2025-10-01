import pytest
from models import Document, db
from datetime import datetime, timedelta

class TestAnalysis:
    """数据分析相关测试"""
    
    def test_get_statistics(self, client, auth_headers, app, test_user):
        """测试获取统计信息"""
        # 创建一些测试文档
        with app.app_context():
            for i in range(5):
                doc = Document(
                    user_id=test_user.id,
                    title=f'文档 {i}',
                    content=f'内容 {i}',
                    source='test',
                    category='科技' if i % 2 == 0 else '财经'
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.get('/api/analysis/stats', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'total_documents' in response.json
        assert response.json['total_documents'] == 5
        assert 'category_distribution' in response.json
    
    def test_get_category_distribution(self, client, auth_headers, app, test_user):
        """测试获取分类分布"""
        # 创建不同分类的文档
        with app.app_context():
            categories = ['科技', '科技', '财经', '体育']
            for category in categories:
                doc = Document(
                    user_id=test_user.id,
                    title='测试',
                    content='内容',
                    source='test',
                    category=category
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.get('/api/analysis/category-distribution', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'distribution' in response.json
        assert response.json['distribution']['科技'] == 2
        assert response.json['distribution']['财经'] == 1
        assert response.json['distribution']['体育'] == 1
    
    def test_get_source_distribution(self, client, auth_headers, app, test_user):
        """测试获取来源分布"""
        with app.app_context():
            sources = ['RSS', 'RSS', '网页抓取', '手动上传']
            for source in sources:
                doc = Document(
                    user_id=test_user.id,
                    title='测试',
                    content='内容',
                    source=source,
                    category='test'
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.get('/api/analysis/source-distribution', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'distribution' in response.json
        assert response.json['distribution']['RSS'] == 2
    
    def test_extract_keywords(self, client, auth_headers, app, test_user):
        """测试关键词提取"""
        # 创建包含特定关键词的文档
        with app.app_context():
            for i in range(3):
                doc = Document(
                    user_id=test_user.id,
                    title='人工智能发展报告',
                    content='人工智能技术在深度学习、自然语言处理、计算机视觉等领域取得重大突破。',
                    source='test',
                    category='科技'
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.post(
            '/api/analysis/keywords',
            headers=auth_headers,
            json={'time_range': 'all', 'topK': 10}
        )
        
        assert response.status_code == 200
        assert 'keywords' in response.json
        assert len(response.json['keywords']) > 0
        assert response.json['document_count'] == 3
    
    def test_get_time_trend(self, client, auth_headers, app, test_user):
        """测试时间趋势分析"""
        with app.app_context():
            # 创建不同时间的文档
            for i in range(3):
                doc = Document(
                    user_id=test_user.id,
                    title=f'文档 {i}',
                    content='内容',
                    source='test',
                    category='test'
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.get('/api/analysis/time-trend?days=7', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'trend' in response.json
        assert response.json['days'] == 7
    
    def test_analysis_report_insufficient_data(self, client, auth_headers, app, test_user):
        """测试数据不足时的分析报告"""
        # 只创建少量文档
        with app.app_context():
            for i in range(5):
                doc = Document(
                    user_id=test_user.id,
                    title=f'文档 {i}',
                    content='内容',
                    source='test',
                    category='test'
                )
                db.session.add(doc)
            db.session.commit()
        
        response = client.get('/api/analysis/report', headers=auth_headers)
        
        assert response.status_code == 400
        assert '数据量不足' in response.json['error']


