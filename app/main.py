"""
EchoSoul AI Platform Main Application
FastAPI application with optimized architecture
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
import sys
import redis
import logging

# Add project root to Python path (优化路径处理)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from config.settings import settings
from app.api import api_router
from app.db import initialize_databases, mysql_db
from app.middleware import create_rate_limit_middleware
from app.core.management.background_tasks import background_task_manager

# 导入所有模型以确保它们被注册到SQLAlchemy
import app.models

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

# Global Redis client
redis_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    global redis_client
    logger.info("🚀 Starting EchoSoul AI Platform Backend Service...")
    
    # Initialize Redis client
    if settings.RATE_LIMIT_REDIS_URL:
        try:
            redis_client = redis.from_url(settings.RATE_LIMIT_REDIS_URL)
            redis_client.ping()
            logger.info("✅ Redis connected for rate limiting")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}, using memory-based rate limiting")
            redis_client = None
    
    # Initialize databases
    try:
        db_results = initialize_databases()
        for db_type, result in db_results.items():
            status = "✅" if result["status"] == "connected" else "❌"
            logger.info(f"{status} {db_type.upper()}: {result['message']}")
        
        # Create MySQL tables if connected
        if db_results.get("mysql", {}).get("status") == "connected":
            try:
                mysql_db.create_tables()
                logger.info("✅ Database tables created successfully")
            except Exception as table_error:
                logger.error(f"❌ Failed to create database tables: {str(table_error)}")
        
        # 启动后台任务
        try:
            await background_task_manager.start_all_tasks()
            logger.info("✅ Background tasks started")
        except Exception as task_error:
            logger.error(f"❌ Failed to start background tasks: {str(task_error)}")
        
        logger.info("🎉 Application startup completed!")
        
    except Exception as e:
        logger.error(f"❌ Application startup error: {str(e)}")
        # 不要因为启动错误而阻止应用运行
        logger.warning("⚠️ Application will continue with limited functionality")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down application...")
    
    # 停止后台任务
    await background_task_manager.stop_all_tasks()
    logger.info("✅ Background tasks stopped")
    
    # Shutdown
    if redis_client:
        redis_client.close()
        logger.info("🔌 Redis connection closed")

# Create FastAPI application with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Platform Backend Service built with FastAPI",
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan
)

# Add rate limiting middleware
if settings.RATE_LIMIT_ENABLED:
    rate_limit_middleware = create_rate_limit_middleware(redis_client)
    app.add_middleware(rate_limit_middleware)
    logger.info("✅ Rate limiting middleware enabled")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    max_age=settings.CORS_MAX_AGE,
)

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
            <p class="status">✅ Optimized Architecture | ✅ Multi-Database Support | ✅ RESTful API</p>
            
            <div class="api-info">
                <h3>📚 API Documentation</h3>
                <ul>
                    <li><a href="/docs">Swagger UI Documentation</a></li>
                    <li><a href="/redoc">ReDoc Documentation</a></li>
                    <li><a href="/api/db/status">Database Status</a></li>
                    <li><a href="/api/auth">Auth API</a></li>
                    <li><a href="/api/users">User Search API</a></li>
                    <li><a href="/api/chat">Chat API</a></li>
                    <li><a href="/api/llm">LLM Chat API</a></li>
                    <li><a href="/api/storage">Storage API</a></li>
                    <li><a href="/api/stats">Statistics API</a></li>
                </ul>
            </div>
            
            <div class="api-info">
                <h3>🗄️ Database Support</h3>
                <ul>
                    <li><strong>MySQL</strong> - Primary relational database</li>
                    <li><strong>Redis</strong> - Caching and session storage</li>
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
        "architecture": "optimized"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )