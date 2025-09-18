"""
API Package
API routes and endpoints
"""

from fastapi import APIRouter
from app.api import users, ai_requests, system_logs, database, stats, auth

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(database.router, prefix="/db", tags=["database"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ai_requests.router, prefix="/ai-requests", tags=["ai-requests"])
api_router.include_router(system_logs.router, prefix="/logs", tags=["system-logs"])
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])

__all__ = ["api_router"]
