"""
Database models for Orca OS using SQLAlchemy.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    DateTime, Text, ForeignKey, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.sql import func
import os
from pathlib import Path

Base = declarative_base()


class User(Base):
    """User profile and preferences."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False, index=True)
    language = Column(String(10), default='en')
    voice_enabled = Column(Boolean, default=False)
    autonomous_mode = Column(Boolean, default=False)
    preferences = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="user", cascade="all, delete-orphan")
    patterns = relationship("Pattern", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """User session tracking."""
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime, nullable=True)
    context_snapshot = Column(JSON, default=dict)
    
    user = relationship("User", back_populates="sessions")
    queries = relationship("Query", back_populates="session", cascade="all, delete-orphan")


class Query(Base):
    """User queries with context."""
    __tablename__ = 'queries'
    
    id = Column(Integer, primary_key=True)
    query_text = Column(Text, nullable=False)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    session_id = Column(String(255), ForeignKey('sessions.session_id'), nullable=False)
    language = Column(String(10), default='en')
    context_data = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    user = relationship("User", back_populates="queries")
    session = relationship("Session", back_populates="queries")
    results = relationship("Result", back_populates="query", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_query_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_query_session', 'session_id'),
    )


class Result(Base):
    """Execution results."""
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    query_id = Column(Integer, ForeignKey('queries.id'), nullable=False)
    command = Column(Text, nullable=False)
    success = Column(Boolean, nullable=False)
    exit_code = Column(Integer)
    stdout = Column(Text)
    stderr = Column(Text)
    execution_time = Column(Float)
    confidence = Column(Float)
    risk_level = Column(String(20))
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    query = relationship("Query", back_populates="results")


class Pattern(Base):
    """Learned patterns from user behavior."""
    __tablename__ = 'patterns'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    pattern_type = Column(String(50), nullable=False)  # 'command', 'time', 'context'
    pattern_data = Column(JSON, nullable=False)
    frequency = Column(Integer, default=1)
    confidence = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="patterns")
    
    __table_args__ = (
        Index('idx_pattern_user_type', 'user_id', 'pattern_type'),
    )


class AutonomousAction(Base):
    """Autonomous actions taken by AI agents."""
    __tablename__ = 'autonomous_actions'
    
    id = Column(Integer, primary_key=True)
    action_type = Column(String(50), nullable=False)  # 'optimize', 'fix', 'predict'
    agent_name = Column(String(100), nullable=False)  # 'process-manager', 'scheduler', etc.
    decision_reason = Column(Text, nullable=False)
    action_taken = Column(Text, nullable=False)
    success = Column(Boolean)
    confidence = Column(Float)
    user_approved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=func.now(), index=True)
    action_metadata = Column(JSON, default=dict)
    
    __table_args__ = (
        Index('idx_autonomous_type_timestamp', 'action_type', 'timestamp'),
    )


class Plugin(Base):
    """Plugin registry."""
    __tablename__ = 'plugins'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    description = Column(Text)
    author = Column(String(255))
    category = Column(String(100))
    enabled = Column(Boolean, default=True)
    installed_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    plugin_metadata = Column(JSON, default=dict)


class MarketplaceItem(Base):
    """Marketplace catalog items."""
    __tablename__ = 'marketplace_items'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(String(255), unique=True, nullable=False, index=True)
    item_type = Column(String(50), nullable=False)  # 'plugin', 'agent', 'theme'
    name = Column(String(255), nullable=False)
    description = Column(Text)
    author = Column(String(255))
    category = Column(String(100))
    version = Column(String(50))
    download_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    item_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AppIntegration(Base):
    """Application-level integrations."""
    __tablename__ = 'app_integrations'
    
    id = Column(Integer, primary_key=True)
    app_name = Column(String(255), nullable=False, index=True)
    app_type = Column(String(50))  # 'desktop', 'web', 'cli'
    integration_type = Column(String(50))  # 'bridge', 'plugin', 'api'
    enabled = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=func.now())


# Database setup
def get_db_path() -> Path:
    """Get database file path."""
    data_dir = os.path.expanduser(os.getenv("ORCA_DATA_DIR", "~/.orca"))
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    return Path(data_dir) / "orca.db"


def get_engine():
    """Get database engine."""
    db_path = get_db_path()
    return create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False
    )


def get_session_factory():
    """Get session factory."""
    return sessionmaker(bind=get_engine())


def get_db() -> Session:
    """Get database session."""
    factory = get_session_factory()
    return factory()


def init_db():
    """Initialize database (create tables)."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

