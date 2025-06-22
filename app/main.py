import os
from fastapi import FastAPI
from .routes import auth_router, protected_router
from .database import init_db
from .logging import setup_logging, get_logger
from .logging.middleware import LoggingMiddleware

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level=log_level)

# Get logger for main application
logger = get_logger("main")

app = FastAPI(title="RBAC Auth System", version="1.0.0")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    logger.info("Starting RBAC Auth System application")
    try:
        init_db()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Shutting down RBAC Auth System application")

# Include routers
app.include_router(auth_router)
app.include_router(protected_router)

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "RBAC Auth System API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy", "service": "RBAC Auth System"}