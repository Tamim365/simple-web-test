from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import os
import json
import boto3
from datetime import datetime
import platform
import psutil
import socket
from typing import Dict, Any

# Initialize FastAPI app
app = FastAPI(
    title="AWS Demo Application",
    description="A sample FastAPI application for AWS EC2 deployment demonstration",
    version="1.0.0"
)

# Data models
class HealthCheck(BaseModel):
    status: str
    timestamp: str
    server_info: Dict[str, Any]

class UserMessage(BaseModel):
    name: str
    email: str
    message: str

# In-memory storage for demo (use RDS/DynamoDB in production)
messages = []

# Utility functions
def get_instance_metadata():
    """Get EC2 instance metadata if available"""
    try:
        import requests
        metadata_url = "http://169.254.169.254/latest/meta-data/"
        response = requests.get(metadata_url + "instance-id", timeout=2)
        if response.status_code == 200:
            return {
                "instance_id": response.text,
                "availability_zone": requests.get(metadata_url + "placement/availability-zone", timeout=2).text,
                "instance_type": requests.get(metadata_url + "instance-type", timeout=2).text,
                "public_ipv4": requests.get(metadata_url + "public-ipv4", timeout=2).text,
                "private_ipv4": requests.get(metadata_url + "local-ipv4", timeout=2).text,
            }
    except:
        pass
    return {"instance_id": "local-development", "note": "Not running on EC2"}

def get_system_info():
    """Get system information"""
    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "cpu_count": psutil.cpu_count(),
        "memory_total": f"{psutil.virtual_memory().total // (1024**3)} GB",
        "memory_available": f"{psutil.virtual_memory().available // (1024**3)} GB",
        "disk_usage": f"{psutil.disk_usage('/').percent}%"
    }

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Main page with AWS demo interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AWS FastAPI Demo</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .api-section {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .endpoint {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 5px;
                margin: 10px 0;
                border-left: 4px solid #4CAF50;
            }
            .method {
                background: #4CAF50;
                color: white;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .method.post {
                background: #2196F3;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #FF9800;
            }
            .button {
                background: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin: 10px 5px;
            }
            .button:hover {
                background: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 AWS FastAPI Demo Application</h1>
                <p>A comprehensive FastAPI application ready for EC2 deployment</p>
            </div>
            
            <div class="api-section">
                <h2>📋 Available API Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <strong>/health</strong> - Health check with server information
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <strong>/aws-info</strong> - EC2 instance metadata and AWS information
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <strong>/system-info</strong> - System and server information
                </div>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <strong>/messages</strong> - Submit a message (JSON: name, email, message)
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <strong>/messages</strong> - Get all messages
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <strong>/load-test</strong> - CPU load test endpoint
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span>
                    <strong>/docs</strong> - Interactive API documentation (Swagger UI)
                </div>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🔧 EC2 Ready</h3>
                    <p>Configured for easy deployment on Amazon EC2 with automatic instance metadata detection</p>
                </div>
                
                <div class="feature-card">
                    <h3>📊 Monitoring</h3>
                    <p>Built-in health checks and system information endpoints for CloudWatch integration</p>
                </div>
                
                <div class="feature-card">
                    <h3>🔒 Production Ready</h3>
                    <p>Includes proper error handling, logging, and security best practices</p>
                </div>
                
                <div class="feature-card">
                    <h3>🎯 Load Testing</h3>
                    <p>Includes endpoints for testing Auto Scaling Groups and Load Balancer behavior</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px;">
                <a href="/docs" class="button">📖 API Documentation</a>
                <a href="/health" class="button">🏥 Health Check</a>
                <a href="/aws-info" class="button">☁️ AWS Info</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for load balancer"""
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        server_info=get_system_info()
    )

@app.get("/aws-info")
async def aws_info():
    """Get AWS EC2 instance information"""
    return {
        "timestamp": datetime.now().isoformat(),
        "ec2_metadata": get_instance_metadata(),
        "environment_variables": {
            "AWS_REGION": os.getenv("AWS_REGION", "not-set"),
            "AWS_AVAILABILITY_ZONE": os.getenv("AWS_AVAILABILITY_ZONE", "not-set"),
            "ENV": os.getenv("ENV", "development")
        }
    }

@app.get("/system-info")
async def system_info():
    """Get detailed system information"""
    return {
        "timestamp": datetime.now().isoformat(),
        "system": get_system_info(),
        "process_info": {
            "pid": os.getpid(),
            "cpu_percent": psutil.Process().cpu_percent(),
            "memory_percent": psutil.Process().memory_percent(),
            "open_files": len(psutil.Process().open_files()),
            "connections": len(psutil.Process().connections())
        }
    }

@app.post("/messages")
async def create_message(message: UserMessage):
    """Create a new message"""
    message_data = {
        "id": len(messages) + 1,
        "name": message.name,
        "email": message.email,
        "message": message.message,
        "timestamp": datetime.now().isoformat(),
        "server_id": get_instance_metadata().get("instance_id", "local")
    }
    messages.append(message_data)
    return {"status": "success", "message": "Message created successfully", "data": message_data}

@app.get("/messages")
async def get_messages():
    """Get all messages"""
    return {
        "total": len(messages),
        "messages": messages,
        "server_id": get_instance_metadata().get("instance_id", "local")
    }

@app.get("/load-test")
async def load_test():
    """CPU intensive endpoint for testing auto scaling"""
    import time
    import threading
    
    def cpu_intensive_task():
        # Simulate CPU intensive work
        start = time.time()
        result = 0
        for i in range(1000000):
            result += i * i
        end = time.time()
        return {"result": result, "duration": end - start}
    
    # Run multiple threads to increase CPU usage
    threads = []
    results = []
    
    for _ in range(4):  # 4 threads
        thread = threading.Thread(target=lambda: results.append(cpu_intensive_task()))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return {
        "message": "Load test completed",
        "results": results,
        "server_id": get_instance_metadata().get("instance_id", "local"),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/error-test")
async def error_test():
    """Test error handling"""
    raise HTTPException(status_code=500, detail="This is a test error for monitoring")

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "path": str(request.url)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "path": str(request.url)}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI AWS Demo Application Starting...")
    print(f"📍 Server Info: {get_system_info()}")
    print(f"☁️ AWS Info: {get_instance_metadata()}")

if __name__ == "__main__":
    # Configuration for production deployment
    uvicorn.run(
        app,
        host="0.0.0.0",  # Listen on all interfaces
        port=80,
        workers=1,  # Single worker for demo, increase for production
        log_level="info",
        access_log=True
    )