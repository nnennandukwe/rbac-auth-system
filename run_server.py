#!/usr/bin/env python3
"""
Startup script for the RBAC Auth System with proper logging configuration.
"""

import os
import uvicorn
from app.logging import setup_logging

def main():
    """Start the RBAC Auth System server with logging"""
    
    # Setup logging before starting the server
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "logs/rbac_auth.log")
    
    print(f"Setting up logging with level: {log_level}")
    print(f"Log file: {log_file}")
    
    setup_logging(log_level=log_level, log_file=log_file)
    
    # Start the server
    print("Starting RBAC Auth System server...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/docs")
    print("Log files will be created in the logs/ directory")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=log_level.lower()
    )

if __name__ == "__main__":
    main()