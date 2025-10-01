import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db
from vector_store import VectorStore
from routes.auth import auth_bp
from routes.documents import documents_bp
from routes.search import search_bp
from routes.analysis import analysis_bp

def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS to allow frontend access
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    jwt = JWTManager(app)
    
    # Initialize vector store
    with app.app_context():
        vector_store = VectorStore(
            model_name=app.config['EMBEDDING_MODEL'],
            index_path=app.config['FAISS_INDEX_PATH']
        )
        app.config['VECTOR_STORE'] = vector_store
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(analysis_bp)
    
    # Error handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token expired',
            'message': 'Please log in again'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'error': 'Invalid token',
            'message': 'Please provide a valid access token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'error': 'Missing token',
            'message': 'Please log in first'
        }), 401
    
    # Health check
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'XU-News-AI-RAG API is running'
        }), 200
    
    # Root route
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({
            'name': 'XU-News-AI-RAG API',
            'version': '1.0.0',
            'description': 'Intelligent Personalized News Knowledge Base System',
            'endpoints': {
                'auth': '/api/auth',
                'documents': '/api/documents',
                'search': '/api/search',
                'analysis': '/api/analysis'
            }
        }), 200
    
    return app

def init_database(app):
    """Initialize database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")

if __name__ == '__main__':
    # Get environment variable
    env = os.getenv('FLASK_ENV', 'development')
    
    # Create application
    app = create_app(env)
    
    # Initialize database
    init_database(app)
    
    # Run application
    port = int(os.getenv('PORT', 5000))
    # Disable reloader to avoid JWT issues
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)

