from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Document
from services.analysis_service import AnalysisService

analysis_bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')

@analysis_bp.route('/report', methods=['GET'])
@jwt_required()
def get_analysis_report():
    """Get data analysis report"""
    current_user_id = get_jwt_identity()
    
    # Get parameters
    time_range = request.args.get('time_range', 'all')  # 7days, 30days, all
    
    # Query all user documents
    documents = Document.query.filter_by(user_id=current_user_id).all()
    
    if len(documents) < 100:
        return jsonify({
            'error': 'Insufficient data',
            'message': 'At least 100 documents are required to generate analysis report',
            'current_count': len(documents)
        }), 400
    
    try:
        # Convert to dictionary format
        docs_dict = [doc.to_dict(include_content=True) for doc in documents]
        
        # Generate analysis report
        report = AnalysisService.generate_summary_report(docs_dict, time_range=time_range)
        
        return jsonify({
            'report': report
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@analysis_bp.route('/keywords', methods=['POST'])
@jwt_required()
def extract_keywords():
    """Extract keywords"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Get parameters
    time_range = data.get('time_range', 'all')
    topK = data.get('topK', 10)
    category = data.get('category', None)
    
    # Build query
    query = Document.query.filter_by(user_id=current_user_id)
    
    if category:
        query = query.filter_by(category=category)
    
    # Filter by time range
    if time_range == '7days':
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        query = query.filter(Document.created_at >= cutoff_date)
    elif time_range == '30days':
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        query = query.filter(Document.created_at >= cutoff_date)
    
    documents = query.all()
    
    if not documents:
        return jsonify({
            'keywords': [],
            'message': 'No matching documents found'
        }), 200
    
    try:
        # Extract text
        texts = []
        for doc in documents:
            text = f"{doc.title} {doc.content}"
            texts.append(text)
        
        # Extract keywords
        keywords = AnalysisService.extract_keywords(texts, topK=topK)
        
        return jsonify({
            'keywords': keywords,
            'document_count': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Keyword extraction failed: {str(e)}'}), 500

@analysis_bp.route('/category-distribution', methods=['GET'])
@jwt_required()
def get_category_distribution():
    """Get category distribution"""
    current_user_id = get_jwt_identity()
    
    # Query all documents
    documents = Document.query.filter_by(user_id=current_user_id).all()
    
    if not documents:
        return jsonify({
            'distribution': {},
            'message': 'No documents found'
        }), 200
    
    try:
        docs_dict = [doc.to_dict() for doc in documents]
        distribution = AnalysisService.analyze_category_distribution(docs_dict)
        
        return jsonify({
            'distribution': distribution,
            'total': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@analysis_bp.route('/source-distribution', methods=['GET'])
@jwt_required()
def get_source_distribution():
    """Get source distribution"""
    current_user_id = get_jwt_identity()
    
    # Query all documents
    documents = Document.query.filter_by(user_id=current_user_id).all()
    
    if not documents:
        return jsonify({
            'distribution': {},
            'message': 'No documents found'
        }), 200
    
    try:
        docs_dict = [doc.to_dict() for doc in documents]
        distribution = AnalysisService.analyze_source_distribution(docs_dict)
        
        return jsonify({
            'distribution': distribution,
            'total': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@analysis_bp.route('/time-trend', methods=['GET'])
@jwt_required()
def get_time_trend():
    """Get time trend"""
    current_user_id = get_jwt_identity()
    
    days = request.args.get('days', 7, type=int)
    
    # Query all documents
    documents = Document.query.filter_by(user_id=current_user_id).all()
    
    if not documents:
        return jsonify({
            'trend': {},
            'message': 'No documents found'
        }), 200
    
    try:
        docs_dict = [doc.to_dict() for doc in documents]
        trend = AnalysisService.analyze_time_trend(docs_dict, days=days)
        
        return jsonify({
            'trend': trend,
            'days': days
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@analysis_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_statistics():
    """Get statistics"""
    current_user_id = get_jwt_identity()
    
    # Calculate various statistics
    total_docs = Document.query.filter_by(user_id=current_user_id).count()
    
    # Statistics by category
    from sqlalchemy import func
    category_stats = db.session.query(
        Document.category,
        func.count(Document.id)
    ).filter_by(user_id=current_user_id).group_by(Document.category).all()
    
    # Statistics by source
    source_stats = db.session.query(
        Document.source,
        func.count(Document.id)
    ).filter_by(user_id=current_user_id).group_by(Document.source).all()
    
    # Recent 7 days
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_docs = Document.query.filter(
        Document.user_id == current_user_id,
        Document.created_at >= week_ago
    ).count()
    
    return jsonify({
        'total_documents': total_docs,
        'recent_7days': recent_docs,
        'category_distribution': dict(category_stats),
        'source_distribution': dict(source_stats),
        'index_size': current_app.config['VECTOR_STORE'].get_index_size()
    }), 200


