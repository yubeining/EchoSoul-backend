"""
EchoSoul AI Platform Backend Service
FastAPI-based HTTP server for AI platform services
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import uvicorn
import os

# Import database and models
from database import get_db, create_tables, test_connection
from models import User, AIRequest, SystemLog
from schemas import (
    UserCreate, UserUpdate, UserResponse,
    AIRequestCreate, AIRequestUpdate, AIRequestResponse,
    SystemLogCreate, SystemLogResponse,
    MessageResponse, DatabaseStatusResponse
)
from crud import (
    get_users, get_user, create_user, update_user, delete_user,
    get_ai_requests, get_ai_request, create_ai_request, update_ai_request, delete_ai_request,
    get_system_logs, create_system_log,
    get_user_count, get_ai_request_count, get_system_log_count
)

# Create FastAPI application
app = FastAPI(
    title="EchoSoul AI Platform Backend Service",
    description="AI Platform Backend Service built with FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        # Test database connection
        connected, message = test_connection()
        if connected:
            # Create tables
            create_tables()
            print("✅ Database connected and tables created successfully")
        else:
            print(f"❌ Database connection failed: {message}")
    except Exception as e:
        print(f"❌ Database initialization error: {str(e)}")

# Pydantic models for request/response
class HealthResponse(BaseModel):
    status: str
    message: str
    version: str

class EchoRequest(BaseModel):
    message: str

class EchoResponse(BaseModel):
    echo: str
    timestamp: str

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint returning HTML welcome page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EchoSoul AI Platform</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { color: #2c3e50; }
            .api-info { background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🚀 EchoSoul AI Platform Backend Service</h1>
            <p>Welcome to EchoSoul AI Platform Backend Service!</p>
            
            <div class="api-info">
                <h3>📚 API Documentation</h3>
                <ul>
                    <li><a href="/docs">Swagger UI Documentation</a></li>
                    <li><a href="/redoc">ReDoc Documentation</a></li>
                    <li><a href="/health">Health Check</a></li>
                    <li><a href="/echo">Echo Service</a></li>
                </ul>
            </div>
            
            <p><strong>Built with FastAPI</strong> - Modern, fast web framework for building APIs with Python 3.7+</p>
        </div>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        message="EchoSoul AI Platform Backend Service is running",
        version="1.0.0"
    )

# Echo endpoint for testing
@app.post("/echo", response_model=EchoResponse)
async def echo_message(request: EchoRequest):
    """Echo service that returns the input message"""
    from datetime import datetime
    return EchoResponse(
        echo=f"EchoSoul says: {request.message}",
        timestamp=datetime.now().isoformat()
    )

# Simple GET endpoint for backward compatibility
@app.get("/hello")
async def hello():
    """Simple hello endpoint"""
    return {"message": "Hello, World! Welcome to EchoSoul AI Platform!"}

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "name": "EchoSoul AI Platform Backend Service",
        "version": "1.0.0",
        "framework": "FastAPI",
        "python_version": os.sys.version,
        "endpoints": {
            "root": "/",
            "health": "/health",
            "echo": "/echo",
            "hello": "/hello",
            "docs": "/docs",
            "redoc": "/redoc",
            "database": "/api/db/status",
            "users": "/api/users",
            "ai_requests": "/api/ai-requests",
            "logs": "/api/logs"
        }
    }

# Database status endpoint
@app.get("/api/db/status", response_model=DatabaseStatusResponse)
async def database_status():
    """Check database connection status"""
    connected, message = test_connection()
    return DatabaseStatusResponse(
        connected=connected,
        message=message,
        tables_created=connected
    )

# User endpoints
@app.get("/api/users", response_model=List[UserResponse])
async def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of users"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@app.post("/api/users", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if username or email already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return create_user(db, user)

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user_endpoint(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """Update user"""
    user = update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/api/users/{user_id}", response_model=MessageResponse)
async def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    """Delete user"""
    if delete_user(db, user_id):
        return MessageResponse(message="User deleted successfully")
    raise HTTPException(status_code=404, detail="User not found")

# AI Request endpoints
@app.get("/api/ai-requests", response_model=List[AIRequestResponse])
async def list_ai_requests(skip: int = 0, limit: int = 100, user_id: int = None, db: Session = Depends(get_db)):
    """Get list of AI requests"""
    requests = get_ai_requests(db, skip=skip, limit=limit, user_id=user_id)
    return requests

@app.post("/api/ai-requests", response_model=AIRequestResponse)
async def create_ai_request_endpoint(request: AIRequestCreate, db: Session = Depends(get_db)):
    """Create a new AI request"""
    return create_ai_request(db, request)

@app.get("/api/ai-requests/{request_id}", response_model=AIRequestResponse)
async def get_ai_request_endpoint(request_id: int, db: Session = Depends(get_db)):
    """Get AI request by ID"""
    request = get_ai_request(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="AI request not found")
    return request

@app.put("/api/ai-requests/{request_id}", response_model=AIRequestResponse)
async def update_ai_request_endpoint(request_id: int, request_update: AIRequestUpdate, db: Session = Depends(get_db)):
    """Update AI request"""
    request = update_ai_request(db, request_id, request_update)
    if not request:
        raise HTTPException(status_code=404, detail="AI request not found")
    return request

@app.delete("/api/ai-requests/{request_id}", response_model=MessageResponse)
async def delete_ai_request_endpoint(request_id: int, db: Session = Depends(get_db)):
    """Delete AI request"""
    if delete_ai_request(db, request_id):
        return MessageResponse(message="AI request deleted successfully")
    raise HTTPException(status_code=404, detail="AI request not found")

# System Log endpoints
@app.get("/api/logs", response_model=List[SystemLogResponse])
async def list_system_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get system logs"""
    logs = get_system_logs(db, skip=skip, limit=limit)
    return logs

@app.post("/api/logs", response_model=SystemLogResponse)
async def create_system_log_endpoint(log: SystemLogCreate, db: Session = Depends(get_db)):
    """Create a system log entry"""
    return create_system_log(db, log)

# Statistics endpoint
@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    return {
        "users": get_user_count(db),
        "ai_requests": get_ai_request_count(db),
        "system_logs": get_system_log_count(db)
    }

if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "echosoul:app",
        host="0.0.0.0",
        port=8080,
        reload=True,  # Enable auto-reload in development
        log_level="info"
    )