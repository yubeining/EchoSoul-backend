"""
EchoSoul AI Platform Database Configuration
MySQL database connection and session management
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# Database configuration
# First connect to MySQL server without database name to create the database
MYSQL_SERVER_URL = "mysql+pymysql://root:kzmtbc6b@echosoul-mysql-mysql.ns-7rdhhsv1.svc:3306"
DATABASE_URL = "mysql+pymysql://root:kzmtbc6b@echosoul-mysql-mysql.ns-7rdhhsv1.svc:3306/echosoul"

# Create database engine
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=True  # Set to False in production
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for table creation
metadata = MetaData()

def get_db():
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database
    """
    Base.metadata.create_all(bind=engine)

def create_database():
    """
    Create the echosoul database if it doesn't exist
    """
    try:
        # Connect to MySQL server without database name
        server_engine = create_engine(MYSQL_SERVER_URL)
        with server_engine.connect() as connection:
            # Create database if it doesn't exist
            connection.execute(text("CREATE DATABASE IF NOT EXISTS echosoul CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            connection.commit()
        server_engine.dispose()
        return True, "Database created successfully"
    except Exception as e:
        return False, f"Database creation failed: {str(e)}"

def test_connection():
    """
    Test database connection
    """
    try:
        # First ensure database exists
        create_success, create_message = create_database()
        if not create_success:
            return False, create_message
        
        # Test connection to the database
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"
