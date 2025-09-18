"""
EchoSoul AI Platform Backend Service
FastAPI-based HTTP server for AI platform services
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import os

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
            "redoc": "/redoc"
        }
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