"""
Database models for the biomedical research platform
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./biomedical_platform.db")

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class
Base = declarative_base()

class QueryLog(Base):
    """Model for logging queries and their results"""
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    sources = Column(JSON, nullable=False)  # List of sources queried
    results = Column(JSON, nullable=True)   # Results from all sources
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), nullable=True)
    processing_time = Column(Integer, nullable=True)  # Processing time in milliseconds
    status = Column(String(50), default="completed")  # completed, failed, partial
    error_message = Column(Text, nullable=True)

class DataProvenance(Base):
    """Model for tracking data provenance"""
    __tablename__ = "data_provenance"
    
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, nullable=False)
    source = Column(String(100), nullable=False)  # pubmed, uniprot, swissadme
    source_url = Column(String(500), nullable=True)
    data_type = Column(String(100), nullable=False)  # article, protein, drug_property
    record_id = Column(String(200), nullable=True)  # PMID, UniProt ID, etc.
    extraction_method = Column(String(100), nullable=False)  # api, web_scraping
    timestamp = Column(DateTime, default=datetime.utcnow)
    data_hash = Column(String(64), nullable=True)  # Hash of the data for integrity

class WorkflowExecution(Base):
    """Model for tracking AI agent workflow executions"""
    __tablename__ = "workflow_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    query_log_id = Column(Integer, nullable=False)
    workflow_type = Column(String(100), nullable=False)  # multi_source, synthesis, etc.
    steps = Column(JSON, nullable=False)  # List of workflow steps
    ai_model = Column(String(100), nullable=True)  # Model used for orchestration
    execution_time = Column(Integer, nullable=True)  # Total execution time
    status = Column(String(50), default="running")  # running, completed, failed
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_database():
    """Initialize the database and create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()