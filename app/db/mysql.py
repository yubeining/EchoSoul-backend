"""
MySQL Database Implementation
MySQL-specific database operations
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from typing import Tuple
import logging
import os

from app.db.base import DatabaseInterface
from config.database import DatabaseConfig

logger = logging.getLogger(__name__)

class MySQLDatabase(DatabaseInterface):
    """MySQL database implementation"""
    
    def __init__(self):
        self.config = DatabaseConfig.get_database_config("mysql")
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()
        self.metadata = MetaData()
    
    def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            # Create database engine with optimized connection pool
            self.engine = create_engine(
                self.config["url"],
                poolclass=QueuePool,
                pool_size=int(os.getenv("DB_POOL_SIZE", 10)),
                max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 20)),
                pool_pre_ping=True,
                pool_recycle=int(os.getenv("DB_POOL_RECYCLE", 3600)),
                echo=os.getenv("DB_ECHO", "false").lower() == "true",
                connect_args={
                    "charset": "utf8mb4",
                    "autocommit": False
                }
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False, 
                autoflush=False, 
                bind=self.engine
            )
            
            logger.info("MySQL database engine created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create MySQL database engine: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MySQL database"""
        if self.engine:
            self.engine.dispose()
            logger.info("MySQL database connection closed")
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test MySQL database connection"""
        try:
            # First ensure database exists
            create_success, create_message = self._create_database()
            if not create_success:
                return False, create_message
            
            # Test connection to the database
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return True, "MySQL connection successful"
                
        except Exception as e:
            return False, f"MySQL connection failed: {str(e)}"
    
    def create_tables(self) -> bool:
        """Create MySQL database tables"""
        try:
            if not self.Base:
                logger.error("Database base not initialized")
                return False
            
            self.Base.metadata.create_all(bind=self.engine)
            logger.info("MySQL tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create MySQL tables: {str(e)}")
            return False
    
    def _create_database(self) -> Tuple[bool, str]:
        """Create the echosoul database if it doesn't exist"""
        try:
            # Connect to MySQL server without database name
            server_engine = create_engine(self.config["server_url"])
            with server_engine.connect() as connection:
                # Create database if it doesn't exist
                connection.execute(text(
                    f"CREATE DATABASE IF NOT EXISTS {self.config['database']} "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                ))
                connection.commit()
            server_engine.dispose()
            return True, "Database created successfully"
            
        except Exception as e:
            return False, f"Database creation failed: {str(e)}"
    
    def get_session(self):
        """Get database session"""
        if not self.SessionLocal:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.SessionLocal()
    
    def get_base(self):
        """Get SQLAlchemy base class"""
        return self.Base

# Global MySQL database instance
mysql_db = MySQLDatabase()
