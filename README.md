# RBAC Auth System

A production-like Role-Based Access Control (RBAC) authentication system built with FastAPI and SQLAlchemy. This project demonstrates complex permission management, secure endpoint enforcement, and comprehensive logging.


## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Option 1: Use the startup script (recommended)](#option-1:-use-the-startup-script-recommended)
- [Option 2: Direct uvicorn](#option-2:-direct-uvicorn)
- [Installation](#installation)
- [Running the Application](#running-the-application)
  - [Method 1: Using the startup script (Recommended)](#method-1:-using-the-startup-script-recommended)
  - [Method 2: Direct uvicorn](#method-2:-direct-uvicorn)
  - [Method 3: With custom logging configuration](#method-3:-with-custom-logging-configuration)
- [Logging System](#logging-system)
  - [Log Files](#log-files)
  - [Log Configuration](#log-configuration)
  - [Testing the Logging System](#testing-the-logging-system)
- [Start the server first](#start-the-server-first)
- [In another terminal, run the test script](#in-another-terminal,-run-the-test-script)
  - [Log Analysis](#log-analysis)
- [View failed login attempts](#view-failed-login-attempts)
- [Monitor permission denials](#monitor-permission-denials)
- [Track API access](#track-api-access)
- [API Documentation](#api-documentation)
- [Default Roles and Permissions](#default-roles-and-permissions)
  - [Roles:](#roles:)
  - [Default Admin User:](#default-admin-user:)
- [Protected Endpoints](#protected-endpoints)
- [Authentication Flow](#authentication-flow)
- [Testing](#testing)
- [Fixed Issues](#fixed-issues)
- [Logging Features Added](#logging-features-added)
- [Project Structure](#project-structure)
- [Environment Configuration](#environment-configuration)

## Features

- JWT-based authentication
- Role-Based Access Control (RBAC)
- Multiple roles per user
- Permission-based endpoint protection
- SQLite database with SQLAlchemy ORM
- **Comprehensive logging system with security and audit trails**
- **Structured JSON logging for easy analysis**
- **Request/response middleware logging**
- **Security event tracking**
- Comprehensive test suite (Admin role only)

## Quick Start

```bash
cd rbac-auth-system
pip install -r requirements.txt

# Option 1: Use the startup script (recommended)
python run_server.py

# Option 2: Direct uvicorn
uvicorn app.main:app --reload
```

## Installation

1. Clone the repository:
```bash
cd rbac-auth-system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Method 1: Using the startup script (Recommended)
```bash
python run_server.py
```

### Method 2: Direct uvicorn
```bash
uvicorn app.main:app --reload
```

### Method 3: With custom logging configuration
```bash
export LOG_LEVEL=DEBUG
export LOG_FILE=logs/custom.log
python run_server.py
```

The API will be available at `http://localhost:8000`

## Logging System

The application includes a comprehensive logging system that tracks:

- **Application Events**: General operations, errors, and performance metrics
- **Security Events**: Authentication, authorization, and security violations
- **Audit Events**: User actions, API access, and data modifications

### Log Files

- `logs/rbac_auth.log` - Main application logs
- `logs/security.log` - Security-related events
- `logs/audit.log` - Audit trail for compliance

### Log Configuration

Set environment variables to configure logging:

```bash
export LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_FILE=logs/rbac_auth.log
```

### Testing the Logging System

Run the logging test script to generate sample log entries:

```bash
# Start the server first
python run_server.py

# In another terminal, run the test script
python test_logging.py
```

This will generate various types of log entries that you can examine in the log files.

### Log Analysis

Logs are formatted as JSON for easy parsing. Example queries:

```bash
# View failed login attempts
grep '"event_type": "LOGIN_FAILED"' logs/security.log | jq '.'

# Monitor permission denials
grep '"event_type": "PERMISSION_DENIED"' logs/security.log

# Track API access
grep '"event_type": "API_ACCESS"' logs/audit.log
```

For detailed logging documentation, see [LOGGING.md](LOGGING.md).

## API Documentation

Once running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Default Roles and Permissions

The system comes pre-seeded with:

### Roles:
- **Admin**: Has all permissions (can_read, can_write, can_delete)
- **Editor**: Has can_read and can_write permissions
- **Viewer**: Has only can_read permission

### Default Admin User:
- Username: `admin`
- Password: `admin123`

## Protected Endpoints

- `GET /admin` - Requires `can_delete` permission
- `GET /edit` - Requires `can_write` permission
- `GET /view` - Requires `can_read` permission

## Authentication Flow

1. Register a new user or use the default admin:
```bash
POST /auth/register
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "role_names": ["Editor"]
}
```

2. Login to get JWT token:
```bash
POST /auth/login
Form data:
- username: admin
- password: admin123
```

3. Use the token to access protected endpoints:
```bash
GET /admin
Headers: Authorization: Bearer <your-token>
```

## Testing

Run the test suite:
```bash
pytest
```

**Note**: Tests are written only for the Admin role, leaving gaps for Editor and Viewer roles to demonstrate testing opportunities.

## Fixed Issues

✅ **Permission Validation Bug Fixed**: The permission validation logic in `app/permissions/dependencies.py` has been corrected. The `check_user_permission` function now properly validates specific permissions instead of using faulty logic.

## Logging Features Added

✅ **Comprehensive Logging System**: Added structured JSON logging throughout the application
✅ **Security Event Tracking**: All authentication and authorization events are logged
✅ **Audit Trail**: Complete audit trail for compliance and monitoring
✅ **Request Middleware**: HTTP request/response logging with performance metrics
✅ **Error Tracking**: Detailed error logging with stack traces
✅ **Log Rotation**: Automatic log rotation to prevent disk space issues

## Project Structure

```
rbac-auth-system/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── routes/          # API endpoints
│   ├── auth/            # Authentication utilities
│   ├── permissions/     # Permission enforcement
│   ├── logging/         # Logging configuration and utilities
│   └── main.py          # FastAPI application
├── tests/               # Test suite
├── logs/                # Log files directory
├── requirements.txt     # Python dependencies
├── run_server.py        # Server startup script
├── test_logging.py      # Logging system test script
├── LOGGING.md          # Detailed logging documentation
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Environment Configuration

Copy `.env.example` to `.env` and customize as needed:

```bash
cp .env.example .env
```

Available configuration options:
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `LOG_FILE`: Main log file path
- `SECRET_KEY`: JWT secret key (change in production)
- `DATABASE_URL`: Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time
---

*Last updated: 2025-07-01 17:31:00 UTC*
