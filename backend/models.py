from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = db.relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    search_history = db.relationship('SearchHistory', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Document(db.Model):
    """Document model"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text)
    source = db.Column(db.String(200))  # RSS, web scraping, manual upload
    source_url = db.Column(db.String(500))
    category = db.Column(db.String(100), index=True)  # Tech, Finance, Sports, etc.
    tags = db.Column(db.String(500))  # Comma-separated tags
    author = db.Column(db.String(200))
    notes = db.Column(db.Text)  # User notes
    vector_id = db.Column(db.Integer, index=True)  # FAISS vector index ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_content=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'summary': self.summary,
            'source': self.source,
            'source_url': self.source_url,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'author': self.author,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        if include_content:
            data['content'] = self.content
        return data

class SearchHistory(db.Model):
    """Search history model"""
    __tablename__ = 'search_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    query = db.Column(db.String(500), nullable=False)
    result_count = db.Column(db.Integer, default=0)
    search_type = db.Column(db.String(50))  # knowledge_base, web_search
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'query': self.query,
            'result_count': self.result_count,
            'search_type': self.search_type,
            'created_at': self.created_at.isoformat()
        }


