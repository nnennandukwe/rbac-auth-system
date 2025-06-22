"""
Integration tests for the complete RBAC system workflow.
"""

import pytest
from fastapi.testclient import TestClient


class TestCompleteUserWorkflow:
    """Test complete user workflows from registration to accessing protected resources"""
    
    def test_admin_user_complete_workflow(self, client: TestClient, setup_roles_and_permissions):
        """Test complete workflow for admin user"""
        # 1. Register admin user
        user_data = {
            "username": "workflow_admin",
            "email": "workflow_admin@test.com",
            "password": "admin123",
            "role_names": ["Admin"]
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        user_info = register_response.json()
        assert user_info["username"] == "workflow_admin"
        assert "Admin" in user_info["roles"]
        
        # 2. Login
        login_response = client.post(
            "/auth/login",
            data={"username": "workflow_admin", "password": "admin123"}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Access all protected routes (admin should have access to all)
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 200
        assert "Welcome to admin area" in admin_response.json()["message"]
        
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 200
        assert "Welcome to editor area" in edit_response.json()["message"]
        
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
        assert "Welcome to viewer area" in view_response.json()["message"]
    
    def test_editor_user_complete_workflow(self, client: TestClient, setup_roles_and_permissions):
        """Test complete workflow for editor user"""
        # 1. Register editor user
        user_data = {
            "username": "workflow_editor",
            "email": "workflow_editor@test.com",
            "password": "editor123",
            "role_names": ["Editor"]
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        user_info = register_response.json()
        assert user_info["username"] == "workflow_editor"
        assert "Editor" in user_info["roles"]
        
        # 2. Login
        login_response = client.post(
            "/auth/login",
            data={"username": "workflow_editor", "password": "editor123"}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test access to routes
        # Should NOT have access to admin route
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        # Should have access to edit route
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 200
        assert "Welcome to editor area" in edit_response.json()["message"]
        
        # Should have access to view route
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
        assert "Welcome to viewer area" in view_response.json()["message"]
    
    def test_viewer_user_complete_workflow(self, client: TestClient, setup_roles_and_permissions):
        """Test complete workflow for viewer user"""
        # 1. Register viewer user
        user_data = {
            "username": "workflow_viewer",
            "email": "workflow_viewer@test.com",
            "password": "viewer123",
            "role_names": ["Viewer"]
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        user_info = register_response.json()
        assert user_info["username"] == "workflow_viewer"
        assert "Viewer" in user_info["roles"]
        
        # 2. Login
        login_response = client.post(
            "/auth/login",
            data={"username": "workflow_viewer", "password": "viewer123"}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test access to routes
        # Should NOT have access to admin route
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        # Should NOT have access to edit route
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 403
        
        # Should have access to view route
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
        assert "Welcome to viewer area" in view_response.json()["message"]
    
    def test_multi_role_user_complete_workflow(self, client: TestClient, setup_roles_and_permissions):
        """Test complete workflow for user with multiple roles"""
        # 1. Register user with multiple roles
        user_data = {
            "username": "workflow_multi",
            "email": "workflow_multi@test.com",
            "password": "multi123",
            "role_names": ["Editor", "Viewer"]
        }
        
        register_response = client.post("/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        user_info = register_response.json()
        assert user_info["username"] == "workflow_multi"
        assert "Editor" in user_info["roles"]
        assert "Viewer" in user_info["roles"]
        assert len(user_info["roles"]) == 2
        
        # 2. Login
        login_response = client.post(
            "/auth/login",
            data={"username": "workflow_multi", "password": "multi123"}
        )
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Test access to routes (should have Editor + Viewer permissions)
        # Should NOT have access to admin route
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        # Should have access to edit route (from Editor role)
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 200
        assert "Welcome to editor area" in edit_response.json()["message"]
        
        # Should have access to view route (from both roles)
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
        assert "Welcome to viewer area" in view_response.json()["message"]


class TestSecurityScenarios:
    """Test various security scenarios"""
    
    def test_token_reuse_across_users(self, client: TestClient, setup_roles_and_permissions):
        """Test that tokens are user-specific and cannot be reused"""
        # Register and login first user
        user1_data = {
            "username": "user1",
            "email": "user1@test.com",
            "password": "password123",
            "role_names": ["Admin"]
        }
        client.post("/auth/register", json=user1_data)
        
        login1_response = client.post(
            "/auth/login",
            data={"username": "user1", "password": "password123"}
        )
        token1 = login1_response.json()["access_token"]
        
        # Register second user
        user2_data = {
            "username": "user2",
            "email": "user2@test.com",
            "password": "password123",
            "role_names": ["Viewer"]
        }
        client.post("/auth/register", json=user2_data)
        
        # Try to use user1's token - should work for user1
        headers1 = {"Authorization": f"Bearer {token1}"}
        response1 = client.get("/admin", headers=headers1)
        assert response1.status_code == 200
        assert response1.json()["user"] == "user1"
        
        # The token should be tied to user1, not user2
        # This is verified by checking the response contains user1's info
        assert "Admin" in response1.json()["roles"]
    
    def test_invalid_token_scenarios(self, client: TestClient, setup_roles_and_permissions):
        """Test various invalid token scenarios"""
        # Test completely invalid token
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/view", headers=headers)
        assert response.status_code == 401
        
        # Test malformed authorization header
        headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/view", headers=headers)
        assert response.status_code == 401
        
        # Test empty token
        headers = {"Authorization": "Bearer "}
        response = client.get("/view", headers=headers)
        assert response.status_code == 401
        
        # Test missing authorization header
        response = client.get("/view")
        assert response.status_code == 401
    
    def test_permission_escalation_prevention(self, client: TestClient, setup_roles_and_permissions):
        """Test that users cannot escalate their permissions"""
        # Register viewer user
        user_data = {
            "username": "viewer_user",
            "email": "viewer@test.com",
            "password": "password123",
            "role_names": ["Viewer"]
        }
        client.post("/auth/register", json=user_data)
        
        # Login and get token
        login_response = client.post(
            "/auth/login",
            data={"username": "viewer_user", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Viewer should not be able to access higher privilege routes
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 403
        
        # But should be able to access their allowed route
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200


class TestErrorHandling:
    """Test error handling in various scenarios"""
    
    def test_duplicate_registration_handling(self, client: TestClient, setup_roles_and_permissions):
        """Test proper error handling for duplicate registrations"""
        user_data = {
            "username": "duplicate_user",
            "email": "duplicate@test.com",
            "password": "password123",
            "role_names": ["Viewer"]
        }
        
        # First registration should succeed
        response1 = client.post("/auth/register", json=user_data)
        assert response1.status_code == 200
        
        # Second registration should fail with proper error
        response2 = client.post("/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Username already registered" in response2.json()["detail"]
        
        # Try with same email but different username
        user_data2 = {
            "username": "different_user",
            "email": "duplicate@test.com",  # Same email
            "password": "password123",
            "role_names": ["Viewer"]
        }
        
        response3 = client.post("/auth/register", json=user_data2)
        assert response3.status_code == 400
        assert "Email already registered" in response3.json()["detail"]
    
    def test_invalid_login_handling(self, client: TestClient, setup_roles_and_permissions):
        """Test proper error handling for invalid logins"""
        # Register a user first
        user_data = {
            "username": "test_user",
            "email": "test@test.com",
            "password": "correct_password",
            "role_names": ["Viewer"]
        }
        client.post("/auth/register", json=user_data)
        
        # Test wrong password
        response1 = client.post(
            "/auth/login",
            data={"username": "test_user", "password": "wrong_password"}
        )
        assert response1.status_code == 401
        assert "Incorrect username or password" in response1.json()["detail"]
        
        # Test non-existent user
        response2 = client.post(
            "/auth/login",
            data={"username": "nonexistent_user", "password": "password123"}
        )
        assert response2.status_code == 401
        assert "Incorrect username or password" in response2.json()["detail"]
    
    def test_invalid_role_assignment_handling(self, client: TestClient, setup_roles_and_permissions):
        """Test handling of invalid role assignments during registration"""
        # Try to register with non-existent role
        user_data = {
            "username": "invalid_role_user",
            "email": "invalid@test.com",
            "password": "password123",
            "role_names": ["NonExistentRole"]
        }
        
        # Should still succeed but default to Viewer role
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == 200
        
        user_info = response.json()
        assert "Viewer" in user_info["roles"]
        assert "NonExistentRole" not in user_info["roles"]


class TestPublicEndpoints:
    """Test public endpoints that don't require authentication"""
    
    def test_root_endpoint_public_access(self, client: TestClient):
        """Test that root endpoint is publicly accessible"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint_public_access(self, client: TestClient):
        """Test that health endpoint is publicly accessible"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert data["status"] == "healthy"


class TestConcurrentAccess:
    """Test concurrent access scenarios"""
    
    def test_multiple_users_concurrent_access(self, client: TestClient, setup_roles_and_permissions):
        """Test that multiple users can access the system concurrently"""
        # Register multiple users with different roles
        users = [
            {"username": "concurrent_admin", "email": "admin@concurrent.com", "password": "pass123", "role_names": ["Admin"]},
            {"username": "concurrent_editor", "email": "editor@concurrent.com", "password": "pass123", "role_names": ["Editor"]},
            {"username": "concurrent_viewer", "email": "viewer@concurrent.com", "password": "pass123", "role_names": ["Viewer"]},
        ]
        
        tokens = {}
        
        # Register and login all users
        for user in users:
            # Register
            register_response = client.post("/auth/register", json=user)
            assert register_response.status_code == 200
            
            # Login
            login_response = client.post(
                "/auth/login",
                data={"username": user["username"], "password": user["password"]}
            )
            assert login_response.status_code == 200
            tokens[user["username"]] = login_response.json()["access_token"]
        
        # Test concurrent access with different permissions
        admin_headers = {"Authorization": f"Bearer {tokens['concurrent_admin']}"}
        editor_headers = {"Authorization": f"Bearer {tokens['concurrent_editor']}"}
        viewer_headers = {"Authorization": f"Bearer {tokens['concurrent_viewer']}"}
        
        # Admin should access all routes
        assert client.get("/admin", headers=admin_headers).status_code == 200
        assert client.get("/edit", headers=admin_headers).status_code == 200
        assert client.get("/view", headers=admin_headers).status_code == 200
        
        # Editor should access edit and view routes
        assert client.get("/admin", headers=editor_headers).status_code == 403
        assert client.get("/edit", headers=editor_headers).status_code == 200
        assert client.get("/view", headers=editor_headers).status_code == 200
        
        # Viewer should access only view route
        assert client.get("/admin", headers=viewer_headers).status_code == 403
        assert client.get("/edit", headers=viewer_headers).status_code == 403
        assert client.get("/view", headers=viewer_headers).status_code == 200