"""
MongoDB Database Implementation
MongoDB-specific document operations (for future use)
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.db.base import DocumentInterface
from config.database import DatabaseConfig

logger = logging.getLogger(__name__)

class MongoDBDatabase(DocumentInterface):
    """MongoDB database implementation"""
    
    def __init__(self):
        self.config = DatabaseConfig.get_database_config("mongodb")
        self.client = None
        self.database = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(
                self.config["url"],
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.database = self.client[self.config["database"]]
            self.connected = True
            logger.info("MongoDB connected successfully")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("MongoDB connection closed")
    
    def test_connection(self) -> tuple[bool, str]:
        """Test MongoDB connection"""
        try:
            if not self.client:
                return False, "MongoDB client not initialized"
            
            self.client.admin.command('ping')
            return True, "MongoDB connection successful"
            
        except Exception as e:
            return False, f"MongoDB connection failed: {str(e)}"
    
    def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        if not self.connected or not self.database:
            raise RuntimeError("MongoDB not connected")
        return self.database[collection_name]
    
    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert single document"""
        try:
            if not self.connected:
                raise RuntimeError("MongoDB not connected")
            
            # Add timestamp
            document["created_at"] = datetime.utcnow()
            
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"MongoDB INSERT ONE error: {str(e)}")
            raise
    
    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents"""
        try:
            if not self.connected:
                raise RuntimeError("MongoDB not connected")
            
            # Add timestamp to all documents
            current_time = datetime.utcnow()
            for doc in documents:
                doc["created_at"] = current_time
            
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
            
        except Exception as e:
            logger.error(f"MongoDB INSERT MANY error: {str(e)}")
            raise
    
    def find_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find single document"""
        try:
            if not self.connected:
                raise RuntimeError("MongoDB not connected")
            
            collection = self.get_collection(collection_name)
            result = collection.find_one(filter_dict)
            
            if result:
                result["_id"] = str(result["_id"])
            
            return result
            
        except Exception as e:
            logger.error(f"MongoDB FIND ONE error: {str(e)}")
            raise
    
    def find_many(self, collection_name: str, filter_dict: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        try:
            if not self.connected:
                raise RuntimeError("MongoDB not connected")
            
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_dict).limit(limit)
            
            results = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"MongoDB FIND MANY error: {str(e)}")
            raise
    
    def update_one(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """Update single document"""
        try:
            if not self.connected:
                raise RuntimeError("MongoDB not connected")
            
            # Add update timestamp
            update_dict["updated_at"] = datetime.utcnow()
            
            collection = self.get_collection(collection_name)
            result = collection.update_one(filter_dict, {"$set": update_dict})
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"MongoDB UPDATE ONE error: {str(e)}")
            raise
    
    def delete_one(self, collection_name: str, filter_dict: Dict[str, Any]) -> bool:
        """Delete single document"""
        try:
            if not self.connected:
                raise RuntimeError("MongoDB not connected")
            
            collection = self.get_collection(collection_name)
            result = collection.delete_one(filter_dict)
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"MongoDB DELETE ONE error: {str(e)}")
            raise

# Global MongoDB database instance
mongodb_db = MongoDBDatabase()
