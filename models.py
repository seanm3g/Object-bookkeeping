"""
Database models for user authentication and configuration storage.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class User(UserMixin, Base):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    config = relationship("UserConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    rules = relationship("UserRule", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class UserConfig(Base):
    """User-specific Shopify configuration."""
    __tablename__ = 'user_configs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    shop_domain = Column(String(255), default='')
    access_token = Column(Text, default='')  # Store encrypted in production
    api_version = Column(String(20), default='2024-01')
    export_path = Column(String(500), default='')
    # Google Sheets OAuth
    gsheets_oauth_token = Column(Text, default='')  # JSON-encoded OAuth token
    gsheets_spreadsheet_id = Column(String(255), default='')
    gsheets_user_email = Column(String(255), default='')  # Store user's Google email
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="config")
    
    def to_dict(self):
        """Convert to dictionary format compatible with existing code."""
        return {
            'shopify': {
                'shop_domain': self.shop_domain or '',
                'access_token': self.access_token or '',
                'api_version': self.api_version or '2024-01'
            },
            'google_sheets': {
                'enabled': bool(self.gsheets_oauth_token),
                'spreadsheet_id': self.gsheets_spreadsheet_id or '',
                'user_email': self.gsheets_user_email or ''
            },
            'export_path': self.export_path or '',
            'product_rules': []
        }
    
    def __repr__(self):
        return f'<UserConfig user_id={self.user_id}>'


class UserRule(Base):
    """User-specific product rules."""
    __tablename__ = 'user_rules'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rule_id = Column(Integer, nullable=False)  # User's rule ID (not database ID)
    description = Column(String(255), nullable=False)
    keywords = Column(JSON, nullable=False)  # List of keywords
    components = Column(JSON, nullable=False)  # List of component objects
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="rules")
    
    def to_dict(self):
        """Convert to dictionary format compatible with existing code."""
        return {
            'id': self.rule_id,
            'description': self.description,
            'keywords': self.keywords,
            'components': self.components
        }
    
    def __repr__(self):
        return f'<UserRule user_id={self.user_id} rule_id={self.rule_id}>'


# Database setup
def get_database_url():
    """Get database URL from environment or use SQLite default."""
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Handle PostgreSQL URLs from hosting platforms
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    # Default to SQLite in instance folder
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    return f'sqlite:///{os.path.join(instance_path, "app.db")}'


def init_db():
    """Initialize database and create tables."""
    engine = create_engine(get_database_url())
    Base.metadata.create_all(engine)
    return engine


def get_db_session(engine=None):
    """Get database session."""
    if engine is None:
        engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    return Session()

