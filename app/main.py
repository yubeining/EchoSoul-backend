"""
EchoSoul AI Platform Main Application
FastAPI application with modular architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
import sys
import redis

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from app.api import api_router
from app.db import initialize_databases, mysql_db
from app.middleware import create_rate_limit_middleware

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Platform Backend Service built with FastAPI",
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL
)

# Initialize Redis client for rate limiting and security monitoring
redis_client = None
if settings.RATE_LIMIT_REDIS_URL:
    try:
        redis_client = redis.from_url(settings.RATE_LIMIT_REDIS_URL)
        redis_client.ping()  # Test connection
        print("✅ Redis connected for rate limiting and security monitoring")
    except Exception as e:
        print(f"⚠️ Redis connection failed: {e}, using memory-based rate limiting")
        redis_client = None

# Security middleware is currently disabled due to compatibility issues

# Add rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    rate_limit_middleware = create_rate_limit_middleware(redis_client)
    app.add_middleware(rate_limit_middleware)
    print("✅ Rate limiting middleware enabled")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Database initialization
@app.on_event("startup")
async def startup_event():
    """Initialize databases on startup"""
    try:
        print("🚀 Starting EchoSoul AI Platform Backend Service...")
        
        # Initialize all databases
        db_results = initialize_databases()
        
        for db_type, result in db_results.items():
            status = "✅" if result["status"] == "connected" else "❌"
            print(f"{status} {db_type.upper()}: {result['message']}")
        
        # Create MySQL tables if connected
        if db_results.get("mysql", {}).get("status") == "connected":
            mysql_db.create_tables()
            print("✅ Database tables created successfully")
        
        print("🎉 Application startup completed!")
        
    except Exception as e:
        print(f"❌ Application startup error: {str(e)}")
        # 不要抛出异常，让应用继续运行

# Include API routes
app.include_router(api_router, prefix="/api")

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
            .status { color: #28a745; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">🚀 EchoSoul AI Platform Backend Service</h1>
            <p>Welcome to EchoSoul AI Platform Backend Service!</p>
            <p class="status">✅ Modular Architecture | ✅ Multi-Database Support | ✅ RESTful API</p>
            
            <div class="api-info">
                <h3>📚 API Documentation</h3>
                <ul>
                    <li><a href="/docs">Swagger UI Documentation</a></li>
                    <li><a href="/redoc">ReDoc Documentation</a></li>
                    <li><a href="/api/db/status">Database Status</a></li>
                    <li><a href="/api/auth">Auth API</a></li>
                    <li><a href="/api/ai-requests">AI Requests API</a></li>
                    <li><a href="/api/logs">System Logs API</a></li>
                    <li><a href="/api/stats">Statistics API</a></li>
                </ul>
            </div>
            
            <div class="api-info">
                <h3>🗄️ Database Support</h3>
                <ul>
                    <li><strong>MySQL</strong> - Primary relational database</li>
                    <li><strong>Redis</strong> - Caching and session storage</li>
                    <li><strong>MongoDB</strong> - Document storage (future)</li>
                </ul>
            </div>
            
            <p><strong>Built with FastAPI</strong> - Modern, fast web framework for building APIs with Python 3.7+</p>
        </div>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "message": "EchoSoul AI Platform Backend Service is running",
        "version": settings.APP_VERSION,
        "architecture": "modular"
    }

# Echo endpoint for testing
@app.post("/echo")
async def echo_message(message: dict):
    """Echo service that returns the input message"""
    from datetime import datetime
    return {
        "echo": f"EchoSoul says: {message.get('message', 'Hello!')}",
        "timestamp": datetime.now().isoformat(),
        "architecture": "modular"
    }

# Simple GET endpoint for backward compatibility
@app.get("/hello")
async def hello():
    """Simple hello endpoint"""
    return {"message": "Hello, World! Welcome to EchoSoul AI Platform!"}

if __name__ == "__main__":
    # Run with uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
