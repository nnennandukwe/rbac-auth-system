# RBAC Authentication System - Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph "Client Layer"
        Client[Client Applications]
        Browser[Web Browser]
        API_Client[API Client]
    end

    subgraph "API Gateway Layer"
        FastAPI[FastAPI Application]
        Middleware[Logging Middleware]
        OAuth2[OAuth2 Password Bearer]
    end

    subgraph "Authentication Layer"
        JWT[JWT Token Service]
        Password[Password Hashing]
        Auth_Routes[Auth Routes]
    end

    subgraph "Authorization Layer"
        RBAC[RBAC Permission System]
        Permission_Deps[Permission Dependencies]
        Protected_Routes[Protected Routes]
    end

    subgraph "Business Logic Layer"
        User_Service[User Management]
        Role_Service[Role Management]
        Permission_Service[Permission Management]
    end

    subgraph "Data Access Layer"
        SQLAlchemy[SQLAlchemy ORM]
        Models[Data Models]
        Database[SQLite Database]
    end

    subgraph "Infrastructure Layer"
        Logging[Logging System]
        Config[Configuration]
        Testing[Test Suite]
    end

    %% Client connections
    Client --> FastAPI
    Browser --> FastAPI
    API_Client --> FastAPI

    %% API Gateway connections
    FastAPI --> Middleware
    FastAPI --> OAuth2
    FastAPI --> Auth_Routes
    FastAPI --> Protected_Routes

    %% Authentication flow
    Auth_Routes --> JWT
    Auth_Routes --> Password
    OAuth2 --> JWT

    %% Authorization flow
    Protected_Routes --> RBAC
    RBAC --> Permission_Deps
    Permission_Deps --> User_Service

    %% Business logic connections
    Auth_Routes --> User_Service
    User_Service --> Role_Service
    Role_Service --> Permission_Service

    %% Data access connections
    User_Service --> SQLAlchemy
    Role_Service --> SQLAlchemy
    Permission_Service --> SQLAlchemy
    SQLAlchemy --> Models
    Models --> Database

    %% Infrastructure connections
    FastAPI --> Logging
    FastAPI --> Config
    Testing --> FastAPI

    %% Styling
    classDef clientLayer fill:#e1f5fe
    classDef apiLayer fill:#f3e5f5
    classDef authLayer fill:#e8f5e8
    classDef businessLayer fill:#fff3e0
    classDef dataLayer fill:#fce4ec
    classDef infraLayer fill:#f1f8e9

    class Client,Browser,API_Client clientLayer
    class FastAPI,Middleware,OAuth2 apiLayer
    class JWT,Password,Auth_Routes,RBAC,Permission_Deps,Protected_Routes authLayer
    class User_Service,Role_Service,Permission_Service businessLayer
    class SQLAlchemy,Models,Database dataLayer
    class Logging,Config,Testing infraLayer
```

## Detailed Component Architecture

### 1. Data Model Relationships

```mermaid
erDiagram
    User ||--o{ UserRole : has
    Role ||--o{ UserRole : assigned_to
    Role ||--o{ RolePermission : has
    Permission ||--o{ RolePermission : granted_to

    User {
        int id PK
        string username UK
        string email UK
        string hashed_password
        datetime created_at
    }

    Role {
        int id PK
        string name UK
        string description
    }

    Permission {
        int id PK
        string name UK
        string description
    }

    UserRole {
        int user_id FK
        int role_id FK
    }

    RolePermission {
        int role_id FK
        int permission_id FK
    }
```

### 2. Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant AuthRoutes
    participant JWT
    participant Database
    participant PasswordHash

    Client->>FastAPI: POST /auth/login
    FastAPI->>AuthRoutes: Route request
    AuthRoutes->>Database: Query user by username
    Database-->>AuthRoutes: Return user data
    AuthRoutes->>PasswordHash: Verify password
    PasswordHash-->>AuthRoutes: Password valid
    AuthRoutes->>JWT: Create access token
    JWT-->>AuthRoutes: Return JWT token
    AuthRoutes-->>FastAPI: Return token response
    FastAPI-->>Client: JWT token + token_type
```

### 3. Authorization Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant OAuth2
    participant JWT
    participant PermissionDeps
    participant Database
    participant ProtectedRoute

    Client->>FastAPI: GET /admin (with Bearer token)
    FastAPI->>OAuth2: Extract token
    OAuth2->>JWT: Verify token
    JWT->>Database: Get user by username
    Database-->>JWT: Return user with roles
    JWT-->>PermissionDeps: Current user
    PermissionDeps->>Database: Check user permissions
    Database-->>PermissionDeps: User permissions
    PermissionDeps-->>ProtectedRoute: Authorized user
    ProtectedRoute-->>FastAPI: Protected resource
    FastAPI-->>Client: Response data
```

### 4. Application Structure

```
rbac-auth-system/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database initialization & seeding
│   │
│   ├── models/                 # SQLAlchemy Data Models
��   │   ├── base.py            # Base model & database session
│   │   ├── user.py            # User model with RBAC methods
│   │   ├── role.py            # Role model
│   │   ├── permission.py      # Permission model
│   │   └── associations.py    # Many-to-many relationship tables
│   │
│   ├── auth/                   # Authentication Components
│   │   ├── jwt.py             # JWT token creation & verification
│   │   └── password.py        # Password hashing utilities
│   │
│   ├── permissions/            # Authorization Components
│   │   └── dependencies.py    # Permission checking dependencies
│   │
│   ├── routes/                 # API Endpoints
│   │   ├── auth.py            # Authentication routes (/auth/*)
│   │   └── protected.py       # Protected routes (/admin, /edit, /view)
│   │
│   └── logging/                # Logging Infrastructure
│       ├── config.py          # Logging configuration
│       └── middleware.py      # Request/response logging middleware
│
├── tests/                      # Test Suite
│   ├── conftest.py            # Test configuration & fixtures
│   ├── test_auth.py           # Authentication tests
│   └── test_rbac.py           # RBAC functionality tests
│
├── alembic/                    # Database Migration Tool
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Key Features & Components

### Core Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Python SQL toolkit and ORM
- **SQLite**: Lightweight database for development
- **JWT**: JSON Web Tokens for stateless authentication
- **Passlib**: Password hashing library with bcrypt
- **Pydantic**: Data validation using Python type annotations

### Security Features
- **JWT-based Authentication**: Stateless token-based auth
- **Password Hashing**: Secure bcrypt password storage
- **Role-Based Access Control**: Flexible permission system
- **OAuth2 Password Bearer**: Standard OAuth2 implementation

### Default RBAC Setup
- **Permissions**: `can_read`, `can_write`, `can_delete`
- **Roles**:
  - Admin: All permissions
  - Editor: `can_read` + `can_write`
  - Viewer: `can_read` only
- **Protected Endpoints**:
  - `/admin` → requires `can_delete`
  - `/edit` → requires `can_write`
  - `/view` → requires `can_read`

### Known Issues
- **Permission Bug**: Intentional bug in `check_user_permission()` function using incorrect logic (`or` instead of proper permission matching)
- **Test Coverage**: Tests only cover Admin role functionality

## Deployment Considerations

### Development
```bash
uvicorn app.main:app --reload
```

### Production Recommendations
- Use PostgreSQL instead of SQLite
- Set proper JWT secret key via environment variables
- Configure proper logging levels
- Use HTTPS for all communications
- Implement rate limiting
- Add input validation and sanitization
- Set up proper error handling and monitoring