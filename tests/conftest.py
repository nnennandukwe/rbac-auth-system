"""
Test configuration and fixtures for RBAC Auth System tests.
"""

import pytest
import asyncio
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.base import Base, get_db
from app.models import User, Role, Permission
from app.models.associations import user_roles, role_permissions
from app.auth import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after each test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def setup_roles_and_permissions(db_session):
    """Set up default roles and permissions"""
    # Create permissions
    permissions = [
        Permission(name="can_read", description="Can read data"),
        Permission(name="can_write", description="Can write data"),
        Permission(name="can_delete", description="Can delete data"),
    ]
    
    for permission in permissions:
        db_session.add(permission)
    
    db_session.commit()
    
    # Create roles
    admin_role = Role(name="Admin", description="Administrator with all permissions")
    editor_role = Role(name="Editor", description="Editor with read and write permissions")
    viewer_role = Role(name="Viewer", description="Viewer with read-only permissions")
    
    # Assign permissions to roles
    admin_role.permissions = permissions  # All permissions
    editor_role.permissions = [p for p in permissions if p.name in ["can_read", "can_write"]]
    viewer_role.permissions = [p for p in permissions if p.name == "can_read"]
    
    db_session.add(admin_role)
    db_session.add(editor_role)
    db_session.add(viewer_role)
    db_session.commit()
    
    return {
        "permissions": {p.name: p for p in permissions},
        "roles": {
            "Admin": admin_role,
            "Editor": editor_role,
            "Viewer": viewer_role
        }
    }


@pytest.fixture(scope="function")
def test_users(db_session, setup_roles_and_permissions):
    """Create test users with different roles"""
    roles = setup_roles_and_permissions["roles"]
    
    # Create test users
    admin_user = User(
        username="test_admin",
        email="admin@test.com",
        hashed_password=get_password_hash("admin123")
    )
    admin_user.roles.append(roles["Admin"])
    
    editor_user = User(
        username="test_editor",
        email="editor@test.com",
        hashed_password=get_password_hash("editor123")
    )
    editor_user.roles.append(roles["Editor"])
    
    viewer_user = User(
        username="test_viewer",
        email="viewer@test.com",
        hashed_password=get_password_hash("viewer123")
    )
    viewer_user.roles.append(roles["Viewer"])
    
    # User with multiple roles
    multi_role_user = User(
        username="test_multi",
        email="multi@test.com",
        hashed_password=get_password_hash("multi123")
    )
    multi_role_user.roles.extend([roles["Editor"], roles["Viewer"]])
    
    # User with no roles
    no_role_user = User(
        username="test_norole",
        email="norole@test.com",
        hashed_password=get_password_hash("norole123")
    )
    
    users = [admin_user, editor_user, viewer_user, multi_role_user, no_role_user]
    for user in users:
        db_session.add(user)
    
    db_session.commit()
    
    return {
        "admin": admin_user,
        "editor": editor_user,
        "viewer": viewer_user,
        "multi_role": multi_role_user,
        "no_role": no_role_user
    }


@pytest.fixture
def auth_headers():
    """Helper function to create authentication headers"""
    def _auth_headers(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}
    return _auth_headers


@pytest.fixture
def login_user():
    """Helper function to login a user and get token"""
    def _login_user(client: TestClient, username: str, password: str) -> str:
        response = client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    return _login_user


@pytest.fixture
def sample_user_data():
    """Sample user registration data"""
    return {
        "valid_user": {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "newpass123",
            "role_names": ["Viewer"]
        },
        "admin_user": {
            "username": "newadmin",
            "email": "newadmin@test.com",
            "password": "adminpass123",
            "role_names": ["Admin"]
        },
        "editor_user": {
            "username": "neweditor",
            "email": "neweditor@test.com",
            "password": "editorpass123",
            "role_names": ["Editor"]
        },
        "multi_role_user": {
            "username": "multirole",
            "email": "multirole@test.com",
            "password": "multipass123",
            "role_names": ["Editor", "Viewer"]
        },
        "invalid_email": {
            "username": "invaliduser",
            "email": "not-an-email",
            "password": "password123",
            "role_names": ["Viewer"]
        },
        "invalid_role": {
            "username": "invalidrole",
            "email": "invalidrole@test.com",
            "password": "password123",
            "role_names": ["NonExistentRole"]
        }
    }