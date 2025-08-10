"""
Database configuration and connection management for Fantasy Football Database.
"""

import os
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/ffb_stats")

# SQLAlchemy setup
Base = declarative_base()
engine: Optional[Engine] = None
SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Get SQLAlchemy engine instance."""
    global engine
    if engine is None:
        engine = create_engine(
            DATABASE_URL,
            echo=os.getenv("DEBUG", "False").lower() == "true",
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
    return engine


def get_session_local() -> sessionmaker:
    """Get SQLAlchemy session maker."""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return SessionLocal


def get_db() -> Session:
    """Get database session."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    # Import models here to avoid circular imports
    import src.models
    Base.metadata.create_all(bind=get_engine())


def setup_database():
    """Initialize database with tables."""
    print("Setting up database...")
    create_tables()
    print("Database setup complete!")


if __name__ == "__main__":
    setup_database()
