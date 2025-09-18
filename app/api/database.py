"""
Database API Routes
Database status and management endpoints
"""

from fastapi import APIRouter
from app.db import mysql_db, redis_cache, mongodb_db
from app.schemas.pydantic_schemas import DatabaseStatusResponse

router = APIRouter()

@router.get("/status", response_model=DatabaseStatusResponse)
async def database_status():
    """Check database connection status"""
    connected, message = mysql_db.test_connection()
    return DatabaseStatusResponse(
        connected=connected,
        message=message,
        tables_created=connected
    )

@router.get("/status/all")
async def all_databases_status():
    """Check status of all configured databases"""
    results = {}
    
    # MySQL status
    mysql_connected, mysql_message = mysql_db.test_connection()
    results["mysql"] = {
        "connected": mysql_connected,
        "message": mysql_message,
        "type": "relational"
    }
    
    # Redis status
    redis_connected, redis_message = redis_cache.test_connection()
    results["redis"] = {
        "connected": redis_connected,
        "message": redis_message,
        "type": "cache"
    }
    
    # MongoDB status
    mongodb_connected, mongodb_message = mongodb_db.test_connection()
    results["mongodb"] = {
        "connected": mongodb_connected,
        "message": mongodb_message,
        "type": "document"
    }
    
    return results
