"""
Database configuration for SpendWise AI.

Sets up the SQLAlchemy engine, session factory, and declarative base
that every model and route depends on.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from a .env file if present.
load_dotenv()

# Default to a local SQLite file named spendwise.db if no DATABASE_URL is set.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./spendwise.db")

# check_same_thread=False is required for SQLite when used with FastAPI,
# since FastAPI can access the DB from multiple threads.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and
    guarantees it is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
