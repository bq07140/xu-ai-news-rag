import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, Document
from services.document_parser import DocumentParser
from datetime import datetime

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@documents_bp.route('/', methods=['GET'])
@jwt_required()
def get_documents():
    """获取文档列表（支持筛选和分页）"""
    current_user_id = get_jwt_identity()
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category', None)
    source = request.args.get('source', None)
    time_range = request.args.get('time_range', None)  # today, 7days, 30days
    sort_by = request.args.get('sort_by', 'created_at')  # created_at, updated_at
    order = request.args.get('order', 'desc')  # asc, desc
    
    # 构建查询
    query = Document.query.filter_by(user_id=current_user_id)
    
    # 按分类筛选
    if category:
        query = query.filter_by(category=category)
    
    # 按来源筛选
    if source:
        query = query.filter_by(source=source)
    
    # 按时间范围筛选
    if time_range:
        now = datetime.utcnow()
        if time_range == 'today':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Document.created_at >= start_time)
        elif time_range == '7days':
            from datetime import timedelta
            start_time = now - timedelta(days=7)
            query = query.filter(Document.created_at >= start_time)
        elif time_range == '30days':
            from datetime import timedelta
            start_time = now - timedelta(days=30)
            query = query.filter(Document.created_at >= start_time)
    
    # 排序
    if sort_by == 'created_at':
        sort_column = Document.created_at
    elif sort_by == 'updated_at':
        sort_column = Document.updated_at
    else:
        sort_column = Document.created_at
    
    if order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'documents': [doc.to_dict() for doc in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@documents_bp.route('/<int:doc_id>', methods=['GET'])
@jwt_required()
def get_document(doc_id):
    """获取单个文档详情"""
    current_user_id = get_jwt_identity()
    
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    
    if not document:
        return jsonify({'error': '文档不存在'}), 404
    
    return jsonify({
        'document': document.to_dict(include_content=True)
    }), 200

@documents_bp.route('/<int:doc_id>', methods=['PUT'])
@jwt_required()
def update_document(doc_id):
    """更新文档元数据"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    
    if not document:
        return jsonify({'error': '文档不存在'}), 404
    
    # 更新允许的字段
    if 'title' in data:
        document.title = data['title']
    if 'summary' in data:
        document.summary = data['summary']
    if 'category' in data:
        document.category = data['category']
    if 'tags' in data:
        # 将标签列表转换为逗号分隔的字符串
        if isinstance(data['tags'], list):
            document.tags = ','.join(data['tags'])
        else:
            document.tags = data['tags']
    if 'source' in data:
        document.source = data['source']
    if 'notes' in data:
        document.notes = data['notes']
    
    try:
        db.session.commit()
        return jsonify({
            'message': '更新成功',
            'document': document.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败：{str(e)}'}), 500

@documents_bp.route('/<int:doc_id>', methods=['DELETE'])
@jwt_required()
def delete_document(doc_id):
    """删除单个文档"""
    current_user_id = get_jwt_identity()
    
    document = Document.query.filter_by(id=doc_id, user_id=current_user_id).first()
    
    if not document:
        return jsonify({'error': '文档不存在'}), 404
    
    try:
        # 从向量库中删除
        vector_store = current_app.config['VECTOR_STORE']
        if document.vector_id is not None:
            vector_store.remove_document(document.id)
        
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除失败：{str(e)}'}), 500

@documents_bp.route('/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete():
    """批量删除文档"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'ids' not in data:
        return jsonify({'error': '缺少文档ID列表'}), 400
    
    doc_ids = data['ids']
    
    if not isinstance(doc_ids, list):
        return jsonify({'error': '文档ID必须是列表'}), 400
    
    try:
        # 查找并删除文档
        documents = Document.query.filter(
            Document.id.in_(doc_ids),
            Document.user_id == current_user_id
        ).all()
        
        vector_store = current_app.config['VECTOR_STORE']
        
        for doc in documents:
            if doc.vector_id is not None:
                vector_store.remove_document(doc.id)
            db.session.delete(doc)
        
        db.session.commit()
        
        return jsonify({
            'message': f'成功删除 {len(documents)} 个文档',
            'deleted_count': len(documents)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量删除失败：{str(e)}'}), 500

@documents_bp.route('/create', methods=['POST'])
@jwt_required()
def create_document():
    """通过文本内容创建文档（用于 n8n 等自动化工具集成）"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # 验证必需字段
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'error': '缺少必需字段: title 和 content'}), 400
    
    try:
        # 创建文档记录
        document = Document(
            user_id=current_user_id,
            title=data.get('title'),
            content=data.get('content'),
            summary=data.get('summary') or (data.get('content')[:200] + '...' if len(data.get('content', '')) > 200 else data.get('content', '')),
            source=data.get('source', 'API创建'),
            source_url=data.get('source_url'),
            category=data.get('category', '未分类'),
            tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', ''),
            author=data.get('author')
        )
        
        db.session.add(document)
        db.session.commit()
        
        # 添加到向量库
        vector_store = current_app.config['VECTOR_STORE']
        text_for_embedding = f"{document.title} {document.content}"
        vector_store.add_document(document.id, text_for_embedding)
        
        # 更新vector_id
        document.vector_id = document.id
        db.session.commit()
        
        return jsonify({
            'message': '创建成功',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建失败：{str(e)}'}), 500

@documents_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_document():
    """上传文档"""
    current_user_id = get_jwt_identity()
    
    # 检查是否有文件
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400
    
    # 保存文件
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    try:
        # 解析文件
        parsed_data = DocumentParser.parse_file(file_path, filename)
        
        if not parsed_data:
            os.remove(file_path)
            return jsonify({'error': '文件解析失败'}), 400
        
        # 创建文档记录
        document = Document(
            user_id=current_user_id,
            title=parsed_data['title'],
            content=parsed_data['content'],
            summary=parsed_data['content'][:200] + '...' if len(parsed_data['content']) > 200 else parsed_data['content'],
            source='手动上传',
            category=request.form.get('category', '未分类')
        )
        
        db.session.add(document)
        db.session.commit()
        
        # 添加到向量库
        vector_store = current_app.config['VECTOR_STORE']
        text_for_embedding = f"{document.title} {document.content}"
        vector_store.add_document(document.id, text_for_embedding)
        
        # 更新vector_id
        document.vector_id = document.id
        db.session.commit()
        
        # 删除临时文件
        os.remove(file_path)
        
        return jsonify({
            'message': '上传成功',
            'document': document.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({'error': f'上传失败：{str(e)}'}), 500

@documents_bp.route('/webhook/n8n', methods=['POST'])
def n8n_webhook():
    """n8n 专用 Webhook（无需认证，用于 n8n 自动抓取数据）"""
    data = request.get_json()
    
    # 可选：验证 webhook secret（建议启用）
    # secret = request.headers.get('X-Webhook-Secret')
    # if secret != 'your-secret-key-here':
    #     return jsonify({'error': '无效的 webhook secret'}), 401
    
    # 使用固定的 n8n 用户（bq07140@gmail.com，用户ID=3）
    n8n_user_id = 3
    
    try:
        # 支持单个或批量插入
        documents_data = data if isinstance(data, list) else [data]
        created_docs = []
        
        for doc_data in documents_data:
            # 验证必需字段
            if 'title' not in doc_data or 'content' not in doc_data:
                continue
            
            # 创建文档
            document = Document(
                user_id=n8n_user_id,
                title=doc_data.get('title'),
                content=doc_data.get('content'),
                summary=doc_data.get('summary') or (doc_data.get('content')[:200] + '...' if len(doc_data.get('content', '')) > 200 else doc_data.get('content', '')),
                source=doc_data.get('source', 'n8n自动抓取'),
                source_url=doc_data.get('source_url'),
                category=doc_data.get('category', '新闻'),
                tags=','.join(doc_data.get('tags', [])) if isinstance(doc_data.get('tags'), list) else doc_data.get('tags', ''),
                author=doc_data.get('author')
            )
            
            db.session.add(document)
            db.session.flush()  # 获取 ID
            
            # 向量化
            vector_store = current_app.config['VECTOR_STORE']
            text_for_embedding = f"{document.title} {document.content}"
            vector_store.add_document(document.id, text_for_embedding)
            
            document.vector_id = document.id
            created_docs.append(document.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'成功创建 {len(created_docs)} 个文档',
            'count': len(created_docs),
            'documents': created_docs
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'创建失败：{str(e)}'
        }), 500

@documents_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    """获取所有分类"""
    current_user_id = get_jwt_identity()
    
    # 查询所有不同的分类
    categories = db.session.query(Document.category).filter_by(user_id=current_user_id).distinct().all()
    category_list = [cat[0] for cat in categories if cat[0]]
    
    return jsonify({
        'categories': category_list
    }), 200

@documents_bp.route('/sources', methods=['GET'])
@jwt_required()
def get_sources():
    """获取所有来源"""
    current_user_id = get_jwt_identity()
    
    # 查询所有不同的来源
    sources = db.session.query(Document.source).filter_by(user_id=current_user_id).distinct().all()
    source_list = [src[0] for src in sources if src[0]]
    
    return jsonify({
        'sources': source_list
    }), 200


