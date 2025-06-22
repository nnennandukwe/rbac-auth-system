"""
Tests for protected routes and role-based access control.
"""

import pytest
from fastapi.testclient import TestClient


class TestAdminRouteAccess:
    """Test access to admin route (/admin) which requires 'can_delete' permission"""
    
    def test_admin_user_can_access_admin_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that admin user can access admin route"""
        token = login_user(client, "test_admin", "admin123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to admin area"
        assert data["user"] == "test_admin"
        assert "Admin" in data["roles"]
    
    def test_editor_user_cannot_access_admin_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that editor user cannot access admin route"""
        token = login_user(client, "test_editor", "editor123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_delete" in response.json()["detail"]
    
    def test_viewer_user_cannot_access_admin_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that viewer user cannot access admin route"""
        token = login_user(client, "test_viewer", "viewer123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_delete" in response.json()["detail"]
    
    def test_multi_role_user_cannot_access_admin_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with Editor+Viewer roles cannot access admin route"""
        token = login_user(client, "test_multi", "multi123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_delete" in response.json()["detail"]
    
    def test_no_role_user_cannot_access_admin_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with no roles cannot access admin route"""
        token = login_user(client, "test_norole", "norole123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_delete" in response.json()["detail"]
    
    def test_unauthenticated_user_cannot_access_admin_route(self, client: TestClient, test_users):
        """Test that unauthenticated user cannot access admin route"""
        response = client.get("/admin")
        assert response.status_code == 401


class TestEditorRouteAccess:
    """Test access to editor route (/edit) which requires 'can_write' permission"""
    
    def test_admin_user_can_access_editor_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that admin user can access editor route"""
        token = login_user(client, "test_admin", "admin123")
        headers = auth_headers(token)
        
        response = client.get("/edit", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to editor area"
        assert data["user"] == "test_admin"
        assert "Admin" in data["roles"]
    
    def test_editor_user_can_access_editor_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that editor user can access editor route"""
        token = login_user(client, "test_editor", "editor123")
        headers = auth_headers(token)
        
        response = client.get("/edit", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to editor area"
        assert data["user"] == "test_editor"
        assert "Editor" in data["roles"]
    
    def test_viewer_user_cannot_access_editor_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that viewer user cannot access editor route"""
        token = login_user(client, "test_viewer", "viewer123")
        headers = auth_headers(token)
        
        response = client.get("/edit", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_write" in response.json()["detail"]
    
    def test_multi_role_user_can_access_editor_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with Editor+Viewer roles can access editor route"""
        token = login_user(client, "test_multi", "multi123")
        headers = auth_headers(token)
        
        response = client.get("/edit", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to editor area"
        assert data["user"] == "test_multi"
        assert "Editor" in data["roles"]
        assert "Viewer" in data["roles"]
    
    def test_no_role_user_cannot_access_editor_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with no roles cannot access editor route"""
        token = login_user(client, "test_norole", "norole123")
        headers = auth_headers(token)
        
        response = client.get("/edit", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_write" in response.json()["detail"]
    
    def test_unauthenticated_user_cannot_access_editor_route(self, client: TestClient, test_users):
        """Test that unauthenticated user cannot access editor route"""
        response = client.get("/edit")
        assert response.status_code == 401


class TestViewerRouteAccess:
    """Test access to viewer route (/view) which requires 'can_read' permission"""
    
    def test_admin_user_can_access_viewer_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that admin user can access viewer route"""
        token = login_user(client, "test_admin", "admin123")
        headers = auth_headers(token)
        
        response = client.get("/view", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to viewer area"
        assert data["user"] == "test_admin"
        assert "Admin" in data["roles"]
    
    def test_editor_user_can_access_viewer_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that editor user can access viewer route"""
        token = login_user(client, "test_editor", "editor123")
        headers = auth_headers(token)
        
        response = client.get("/view", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to viewer area"
        assert data["user"] == "test_editor"
        assert "Editor" in data["roles"]
    
    def test_viewer_user_can_access_viewer_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that viewer user can access viewer route"""
        token = login_user(client, "test_viewer", "viewer123")
        headers = auth_headers(token)
        
        response = client.get("/view", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to viewer area"
        assert data["user"] == "test_viewer"
        assert "Viewer" in data["roles"]
    
    def test_multi_role_user_can_access_viewer_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with Editor+Viewer roles can access viewer route"""
        token = login_user(client, "test_multi", "multi123")
        headers = auth_headers(token)
        
        response = client.get("/view", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Welcome to viewer area"
        assert data["user"] == "test_multi"
        assert "Editor" in data["roles"]
        assert "Viewer" in data["roles"]
    
    def test_no_role_user_cannot_access_viewer_route(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with no roles cannot access viewer route"""
        token = login_user(client, "test_norole", "norole123")
        headers = auth_headers(token)
        
        response = client.get("/view", headers=headers)
        assert response.status_code == 403
        assert "does not have required permission: can_read" in response.json()["detail"]
    
    def test_unauthenticated_user_cannot_access_viewer_route(self, client: TestClient, test_users):
        """Test that unauthenticated user cannot access viewer route"""
        response = client.get("/view")
        assert response.status_code == 401


class TestRolePermissionMatrix:
    """Test the complete role-permission matrix"""
    
    def test_admin_role_permissions(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that Admin role has all permissions (can_read, can_write, can_delete)"""
        token = login_user(client, "test_admin", "admin123")
        headers = auth_headers(token)
        
        # Admin should access all routes
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 200
        
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 200
        
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
    
    def test_editor_role_permissions(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that Editor role has can_read and can_write permissions only"""
        token = login_user(client, "test_editor", "editor123")
        headers = auth_headers(token)
        
        # Editor should NOT access admin route (requires can_delete)
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        # Editor should access edit route (requires can_write)
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 200
        
        # Editor should access view route (requires can_read)
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
    
    def test_viewer_role_permissions(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that Viewer role has can_read permission only"""
        token = login_user(client, "test_viewer", "viewer123")
        headers = auth_headers(token)
        
        # Viewer should NOT access admin route (requires can_delete)
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        # Viewer should NOT access edit route (requires can_write)
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 403
        
        # Viewer should access view route (requires can_read)
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
    
    def test_multi_role_permissions(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with multiple roles gets combined permissions"""
        token = login_user(client, "test_multi", "multi123")
        headers = auth_headers(token)
        
        # Multi-role user (Editor+Viewer) should NOT access admin route
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        # Multi-role user should access edit route (from Editor role)
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 200
        
        # Multi-role user should access view route (from both roles)
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 200
    
    def test_no_role_permissions(self, client: TestClient, test_users, login_user, auth_headers):
        """Test that user with no roles has no permissions"""
        token = login_user(client, "test_norole", "norole123")
        headers = auth_headers(token)
        
        # User with no roles should not access any protected route
        admin_response = client.get("/admin", headers=headers)
        assert admin_response.status_code == 403
        
        edit_response = client.get("/edit", headers=headers)
        assert edit_response.status_code == 403
        
        view_response = client.get("/view", headers=headers)
        assert view_response.status_code == 403


class TestRouteResponseFormat:
    """Test that protected routes return correct response format"""
    
    def test_admin_route_response_format(self, client: TestClient, test_users, login_user, auth_headers):
        """Test admin route response format"""
        token = login_user(client, "test_admin", "admin123")
        headers = auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0
    
    def test_editor_route_response_format(self, client: TestClient, test_users, login_user, auth_headers):
        """Test editor route response format"""
        token = login_user(client, "test_editor", "editor123")
        headers = auth_headers(token)
        
        response = client.get("/edit", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0
    
    def test_viewer_route_response_format(self, client: TestClient, test_users, login_user, auth_headers):
        """Test viewer route response format"""
        token = login_user(client, "test_viewer", "viewer123")
        headers = auth_headers(token)
        
        response = client.get("/view", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "user" in data
        assert "roles" in data
        assert isinstance(data["roles"], list)
        assert len(data["roles"]) > 0