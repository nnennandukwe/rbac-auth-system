import logging
import logging.config
import os
from datetime import datetime
from typing import Dict, Any
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if they exist
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'username'):
            log_entry['username'] = record.username
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        if hasattr(record, 'permission'):
            log_entry['permission'] = record.permission
        if hasattr(record, 'roles'):
            log_entry['roles'] = record.roles
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)


def setup_logging(log_level: str = "INFO", log_file: str = "logs/rbac_auth.log") -> None:
    """Setup logging configuration for the application"""
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Define logging configuration
    config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(levelname)s - %(name)s - %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "json",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "security": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/security.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
            },
            "audit": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/audit.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
            },
        },
        "loggers": {
            "rbac_auth": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "rbac_auth.security": {
                "level": "INFO",
                "handlers": ["security", "console"],
                "propagate": False,
            },
            "rbac_auth.audit": {
                "level": "INFO",
                "handlers": ["audit", "console"],
                "propagate": False,
            },
            "rbac_auth.database": {
                "level": log_level,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "rbac_auth.auth": {
                "level": log_level,
                "handlers": ["console", "file", "security"],
                "propagate": False,
            },
            "rbac_auth.permissions": {
                "level": log_level,
                "handlers": ["console", "file", "audit"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }
    
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(f"rbac_auth.{name}")


# Security event types for consistent logging
class SecurityEvents:
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    REGISTRATION_SUCCESS = "REGISTRATION_SUCCESS"
    REGISTRATION_FAILED = "REGISTRATION_FAILED"
    TOKEN_CREATED = "TOKEN_CREATED"
    TOKEN_VALIDATION_FAILED = "TOKEN_VALIDATION_FAILED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"


# Audit event types
class AuditEvents:
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    ROLE_ASSIGNED = "ROLE_ASSIGNED"
    ROLE_REMOVED = "ROLE_REMOVED"
    PERMISSION_CHECK = "PERMISSION_CHECK"
    DATABASE_INITIALIZED = "DATABASE_INITIALIZED"
    API_ACCESS = "API_ACCESS"


def log_security_event(
    event_type: str,
    message: str,
    username: str = None,
    user_id: int = None,
    ip_address: str = None,
    additional_data: Dict[str, Any] = None
) -> None:
    """Log security-related events"""
    logger = get_logger("security")
    
    extra = {
        "event_type": event_type,
        "username": username,
        "user_id": user_id,
        "ip_address": ip_address,
    }
    
    if additional_data:
        extra.update(additional_data)
    
    logger.info(message, extra=extra)


def log_audit_event(
    event_type: str,
    message: str,
    username: str = None,
    user_id: int = None,
    resource: str = None,
    additional_data: Dict[str, Any] = None
) -> None:
    """Log audit events"""
    logger = get_logger("audit")
    
    extra = {
        "event_type": event_type,
        "username": username,
        "user_id": user_id,
        "resource": resource,
    }
    
    if additional_data:
        extra.update(additional_data)
    
    logger.info(message, extra=extra)