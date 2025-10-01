from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Document, SearchHistory
from services.search_service import WebSearchService, LLMService
from datetime import datetime

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/semantic', methods=['POST'])
@jwt_required()
def semantic_search():
    """全文检索（基于 SQLite）"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': '缺少查询内容'}), 400
    
    search_query = data['query']
    limit = data.get('k', current_app.config['MAX_SEARCH_RESULTS'])
    
    try:
        # 使用 jieba 分词提取关键词
        import jieba
        keywords = list(jieba.cut_for_search(search_query))
        # 过滤停用词
        stopwords = {'的', '了', '是', '在', '有', '和', '与', '及', '或', '等', '啊', '吗', '呢'}
        keywords = [k for k in keywords if k not in stopwords and len(k) > 1]
        
        # 构建 SQL 查询
        if not keywords:
            # 如果没有关键词，使用原始查询
            keywords = [search_query]
        
        # 使用 LIKE 进行全文搜索
        conditions = []
        for keyword in keywords[:5]:  # 最多使用前5个关键词
            conditions.append(Document.title.like(f'%{keyword}%'))
            conditions.append(Document.content.like(f'%{keyword}%'))
        
        # 组合查询条件（OR）
        from sqlalchemy import or_
        query_filter = or_(*conditions)
        
        # 执行查询
        documents = Document.query.filter_by(user_id=current_user_id)\
            .filter(query_filter)\
            .order_by(Document.created_at.desc())\
            .limit(limit)\
            .all()
        
        # 格式化结果
        results = []
        for doc in documents:
            doc_dict = doc.to_dict()
            # 计算匹配度（简单统计匹配的关键词数量）
            match_count = sum(1 for k in keywords if k in doc.title or k in doc.content)
            doc_dict['match_score'] = match_count / len(keywords) if keywords else 0
            doc_dict['matched_keywords'] = [k for k in keywords if k in doc.title or k in doc.content]
            results.append(doc_dict)
        
        # 按匹配度排序
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        # 记录搜索历史
        history = SearchHistory(
            user_id=current_user_id,
            query=search_query,
            result_count=len(results),
            search_type='knowledge_base'
        )
        db.session.add(history)
        db.session.commit()
        
        # 判断是否需要触发联网搜索
        trigger_web_search = len(results) < 3
        
        return jsonify({
            'query': search_query,
            'keywords': keywords[:5],
            'results': results,
            'count': len(results),
            'trigger_web_search': trigger_web_search
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'搜索失败：{str(e)}'}), 500

@search_bp.route('/web', methods=['POST'])
@jwt_required()
def web_search():
    """联网搜索"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': '缺少查询内容'}), 400
    
    search_query = data['query']
    num_results = data.get('num_results', 3)
    
    try:
        # 执行网络搜索
        search_service = WebSearchService(
            api_key=current_app.config.get('SEARCH_API_KEY', ''),
            api_url=current_app.config.get('SEARCH_API_URL', '')
        )
        search_results = search_service.search(search_query, num_results=num_results)
        
        # 使用LLM总结结果
        llm_service = LLMService()
        summary = llm_service.summarize_search_results(search_query, search_results)
        
        # 记录搜索历史
        history = SearchHistory(
            user_id=current_user_id,
            query=search_query,
            result_count=len(search_results),
            search_type='web_search'
        )
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'query': search_query,
            'results': search_results,
            'summary': summary,
            'count': len(search_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'网络搜索失败：{str(e)}'}), 500

@search_bp.route('/combined', methods=['POST'])
@jwt_required()
def combined_search():
    """组合搜索（先知识库，不足时联网）"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({'error': '缺少查询内容'}), 400
    
    search_query = data['query']
    limit = data.get('k', current_app.config['MAX_SEARCH_RESULTS'])
    
    try:
        # 1. 先从知识库搜索（SQLite 全文搜索）
        import jieba
        from sqlalchemy import or_
        
        keywords = list(jieba.cut_for_search(search_query))
        stopwords = {'的', '了', '是', '在', '有', '和', '与', '及', '或', '等', '啊', '吗', '呢'}
        keywords = [k for k in keywords if k not in stopwords and len(k) > 1]
        
        if not keywords:
            keywords = [search_query]
        
        # 构建搜索条件
        conditions = []
        for keyword in keywords[:5]:
            conditions.append(Document.title.like(f'%{keyword}%'))
            conditions.append(Document.content.like(f'%{keyword}%'))
        
        query_filter = or_(*conditions)
        
        # 执行查询
        documents = Document.query.filter_by(user_id=current_user_id)\
            .filter(query_filter)\
            .order_by(Document.created_at.desc())\
            .limit(limit)\
            .all()
        
        # 格式化结果
        kb_results = []
        for doc in documents:
            doc_dict = doc.to_dict()
            match_count = sum(1 for k in keywords if k in doc.title or k in doc.content)
            doc_dict['match_score'] = match_count / len(keywords) if keywords else 0
            doc_dict['matched_keywords'] = [k for k in keywords if k in doc.title or k in doc.content]
            kb_results.append(doc_dict)
        
        # 按匹配度排序
        kb_results.sort(key=lambda x: x['match_score'], reverse=True)
        
        response_data = {
            'query': search_query,
            'keywords': keywords[:5],
            'knowledge_base_results': kb_results,
            'kb_count': len(kb_results),
            'web_search_triggered': False
        }
        
        # 2. 判断是否需要联网搜索
        if len(kb_results) < 3:
            # 执行网络搜索
            search_service = WebSearchService(
                api_key=current_app.config.get('SEARCH_API_KEY', ''),
                api_url=current_app.config.get('SEARCH_API_URL', '')
            )
            web_results = search_service.search(search_query, num_results=3)
            
            # 使用LLM总结
            llm_service = LLMService()
            summary = llm_service.summarize_search_results(search_query, web_results)
            
            response_data['web_search_triggered'] = True
            response_data['web_results'] = web_results
            response_data['web_summary'] = summary
            response_data['web_count'] = len(web_results)
            
            # 记录搜索历史
            history = SearchHistory(
                user_id=current_user_id,
                query=search_query,
                result_count=len(kb_results) + len(web_results),
                search_type='combined'
            )
        else:
            # 只记录知识库搜索
            history = SearchHistory(
                user_id=current_user_id,
                query=search_query,
                result_count=len(kb_results),
                search_type='knowledge_base'
            )
        
        db.session.add(history)
        db.session.commit()
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': f'搜索失败：{str(e)}'}), 500

@search_bp.route('/history', methods=['GET'])
@jwt_required()
def get_search_history():
    """获取搜索历史"""
    current_user_id = get_jwt_identity()
    
    limit = request.args.get('limit', 10, type=int)
    
    # 查询最近的搜索历史
    history = db.session.query(SearchHistory)\
        .filter_by(user_id=current_user_id)\
        .order_by(SearchHistory.created_at.desc())\
        .limit(limit)\
        .all()
    
    return jsonify({
        'history': [h.to_dict() for h in history]
    }), 200

@search_bp.route('/history/<int:history_id>', methods=['DELETE'])
@jwt_required()
def delete_search_history(history_id):
    """删除搜索历史"""
    current_user_id = get_jwt_identity()
    
    history = db.session.query(SearchHistory).filter_by(id=history_id, user_id=current_user_id).first()
    
    if not history:
        return jsonify({'error': '历史记录不存在'}), 404
    
    try:
        db.session.delete(history)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败：{str(e)}'}), 500


