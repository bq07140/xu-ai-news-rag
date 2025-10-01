import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class"""
    
    # Flask configuration
    SECRET_KEY = 'xu-news-rag-secret-key-fixed-2025-10-01'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///xu_news_rag.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration - using fixed key
    JWT_SECRET_KEY = 'xu-news-rag-jwt-secret-key-fixed-2025-10-01'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # CORS configuration
    CORS_HEADERS = 'Content-Type'
    
    # Embedding model configuration
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    
    # Search API configuration
    SEARCH_API_KEY = os.getenv('SEARCH_API_KEY', '')
    SEARCH_API_URL = os.getenv('SEARCH_API_URL', '')
    
    # Retrieval configuration
    SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.6'))
    MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', '10'))
    
    # File upload configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', '52428800'))  # 50MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'xlsx', 'xls', 'md'}
    
    # FAISS vector store path
    FAISS_INDEX_PATH = 'faiss_index'
    VECTOR_DIM = 384  # Vector dimension for all-MiniLM-L6-v2

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

