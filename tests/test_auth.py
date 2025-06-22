"""
Tests for authentication endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_user_with_viewer_role(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test successful user registration with Viewer role"""
        user_data = sample_user_data["valid_user"]
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "Viewer" in data["roles"]
        assert "id" in data
    
    def test_register_user_with_admin_role(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test successful user registration with Admin role"""
        user_data = sample_user_data["admin_user"]
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert "Admin" in data["roles"]
    
    def test_register_user_with_editor_role(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test successful user registration with Editor role"""
        user_data = sample_user_data["editor_user"]
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert "Editor" in data["roles"]
    
    def test_register_user_with_multiple_roles(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test user registration with multiple roles"""
        user_data = sample_user_data["multi_role_user"]
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == user_data["username"]
        assert "Editor" in data["roles"]
        assert "Viewer" in data["roles"]
        assert len(data["roles"]) == 2
    
    def test_register_user_no_roles_defaults_to_viewer(self, client: TestClient, setup_roles_and_permissions):
        """Test that user with no specified roles gets Viewer role by default"""
        user_data = {
            "username": "defaultuser",
            "email": "default@test.com",
            "password": "password123",
            "role_names": []
        }
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "Viewer" in data["roles"]
    
    def test_register_user_with_invalid_role(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test user registration with non-existent role defaults to Viewer"""
        user_data = sample_user_data["invalid_role"]
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "Viewer" in data["roles"]  # Should default to Viewer
    
    def test_register_duplicate_username(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test registration with duplicate username fails"""
        user_data = sample_user_data["valid_user"]
        
        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration with same username should fail
        response2 = client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Username already registered" in response2.json()["detail"]
    
    def test_register_duplicate_email(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test registration with duplicate email fails"""
        user_data1 = sample_user_data["valid_user"]
        user_data2 = {
            "username": "differentuser",
            "email": user_data1["email"],  # Same email
            "password": "password123",
            "role_names": ["Viewer"]
        }
        
        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data1)
        assert response1.status_code == 200
        
        # Second registration with same email should fail
        response2 = client.post("/auth/register", json=user_data2)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
    
    def test_register_invalid_email_format(self, client: TestClient, setup_roles_and_permissions, sample_user_data):
        """Test registration with invalid email format fails"""
        user_data = sample_user_data["invalid_email"]
        response = client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422  # Validation error


class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_admin_user_success(self, client: TestClient, test_users, login_user):
        """Test successful login for admin user"""
        token = login_user(client, "test_admin", "admin123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_editor_user_success(self, client: TestClient, test_users, login_user):
        """Test successful login for editor user"""
        token = login_user(client, "test_editor", "editor123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_viewer_user_success(self, client: TestClient, test_users, login_user):
        """Test successful login for viewer user"""
        token = login_user(client, "test_viewer", "viewer123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_multi_role_user_success(self, client: TestClient, test_users, login_user):
        """Test successful login for user with multiple roles"""
        token = login_user(client, "test_multi", "multi123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_user_with_no_roles(self, client: TestClient, test_users, login_user):
        """Test login for user with no roles still works"""
        token = login_user(client, "test_norole", "norole123")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_invalid_username(self, client: TestClient, test_users):
        """Test login with non-existent username fails"""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client: TestClient, test_users):
        """Test login with wrong password fails"""
        response = client.post(
            "/auth/login",
            data={"username": "test_admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_empty_credentials(self, client: TestClient, test_users):
        """Test login with empty credentials fails"""
        response = client.post(
            "/auth/login",
            data={"username": "", "password": ""}
        )
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_credentials(self, client: TestClient, test_users):
        """Test login with missing credentials fails"""
        response = client.post("/auth/login", data={})
        assert response.status_code == 422  # Validation error
    
    def test_login_response_format(self, client: TestClient, test_users):
        """Test that login response has correct format"""
        response = client.post(
            "/auth/login",
            data={"username": "test_admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0


class TestTokenValidation:
    """Test JWT token validation"""
    
    def test_valid_token_access(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that valid token allows access to protected endpoints"""
        token = login_user(client, "test_admin", "admin123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 200
    
    def test_invalid_token_access(self, client: TestClient, test_users, auth_headers):
        """Test that invalid token denies access"""
        headers = auth_headers("invalid_token_here")
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 401
    
    def test_missing_token_access(self, client: TestClient, test_users):
        """Test that missing token denies access"""
        response = client.get("/admin")
        assert response.status_code == 401
    
    def test_malformed_token_header(self, client: TestClient, test_users):
        """Test that malformed authorization header denies access"""
        headers = {"Authorization": "InvalidFormat token_here"}
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 401
    
    def test_empty_token(self, client: TestClient, test_users, auth_headers):
        """Test that empty token denies access"""
        headers = auth_headers("")
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 401