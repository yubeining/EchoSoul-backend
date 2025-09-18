"""
Database Base Classes
Abstract base classes for different database types
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

class DatabaseInterface(ABC):
    """Abstract database interface"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to database"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from database"""
        pass
    
    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Test database connection"""
        pass
    
    @abstractmethod
    def create_tables(self) -> bool:
        """Create database tables"""
        pass

class CRUDInterface(ABC):
    """Abstract CRUD interface"""
    
    @abstractmethod
    def create(self, db: Session, obj_in: Any) -> Any:
        """Create new record"""
        pass
    
    @abstractmethod
    def get(self, db: Session, id: int) -> Optional[Any]:
        """Get record by ID"""
        pass
    
    @abstractmethod
    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[Any]:
        """Get multiple records"""
        pass
    
    @abstractmethod
    def update(self, db: Session, db_obj: Any, obj_in: Any) -> Any:
        """Update record"""
        pass
    
    @abstractmethod
    def delete(self, db: Session, id: int) -> bool:
        """Delete record"""
        pass

class CacheInterface(ABC):
    """Abstract cache interface for Redis"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set key-value pair"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        pass

class DocumentInterface(ABC):
    """Abstract document interface for MongoDB"""
    
    @abstractmethod
    def insert_one(self, document: Dict[str, Any]) -> str:
        """Insert single document"""
        pass
    
    @abstractmethod
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents"""
        pass
    
    @abstractmethod
    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find single document"""
        pass
    
    @abstractmethod
    def find_many(self, filter_dict: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        pass
    
    @abstractmethod
    def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """Update single document"""
        pass
    
    @abstractmethod
    def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """Delete single document"""
        pass
