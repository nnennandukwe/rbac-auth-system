"""
Tests for permission system and dependencies.
"""

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import User, Role, Permission
from app.permissions.dependencies import check_user_permission, require_permission
from app.auth import get_password_hash


class TestCheckUserPermission:
    """Test the check_user_permission function"""
    
    def test_user_with_permission_returns_true(self, db_session: Session, setup_roles_and_permissions):
        """Test that user with required permission returns True"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Admin"])
        db_session.add(user)
        db_session.commit()
        
        assert check_user_permission(user, "can_read") is True
        assert check_user_permission(user, "can_write") is True
        assert check_user_permission(user, "can_delete") is True
    
    def test_user_without_permission_returns_false(self, db_session: Session, setup_roles_and_permissions):
        """Test that user without required permission returns False"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Viewer"])
        db_session.add(user)
        db_session.commit()
        
        assert check_user_permission(user, "can_read") is True
        assert check_user_permission(user, "can_write") is False
        assert check_user_permission(user, "can_delete") is False
    
    def test_user_with_no_roles_returns_false(self, db_session: Session):
        """Test that user with no roles returns False for any permission"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        assert check_user_permission(user, "can_read") is False
        assert check_user_permission(user, "can_write") is False
        assert check_user_permission(user, "can_delete") is False
    
    def test_user_with_multiple_roles(self, db_session: Session, setup_roles_and_permissions):
        """Test user with multiple roles gets combined permissions"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.extend([roles["Editor"], roles["Viewer"]])
        db_session.add(user)
        db_session.commit()
        
        assert check_user_permission(user, "can_read") is True
        assert check_user_permission(user, "can_write") is True
        assert check_user_permission(user, "can_delete") is False
    
    def test_nonexistent_permission_returns_false(self, db_session: Session, setup_roles_and_permissions):
        """Test that checking for nonexistent permission returns False"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Admin"])
        db_session.add(user)
        db_session.commit()
        
        assert check_user_permission(user, "nonexistent_permission") is False


class TestRequirePermissionDependency:
    """Test the require_permission dependency factory"""
    
    def test_require_permission_creates_dependency(self):
        """Test that require_permission returns a callable dependency"""
        dependency = require_permission("can_read")
        assert callable(dependency)
    
    def test_permission_dependency_with_valid_permission(self, db_session: Session, setup_roles_and_permissions):
        """Test permission dependency with user who has required permission"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Admin"])
        db_session.add(user)
        db_session.commit()
        
        dependency = require_permission("can_read")
        
        # This should not raise an exception
        result = dependency(current_user=user, db=db_session)
        assert result == user
    
    def test_permission_dependency_with_invalid_permission(self, db_session: Session, setup_roles_and_permissions):
        """Test permission dependency with user who lacks required permission"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Viewer"])
        db_session.add(user)
        db_session.commit()
        
        dependency = require_permission("can_delete")
        
        # This should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            dependency(current_user=user, db=db_session)
        
        assert exc_info.value.status_code == 403
        assert "does not have required permission: can_delete" in str(exc_info.value.detail)
    
    def test_permission_dependency_with_no_roles(self, db_session: Session):
        """Test permission dependency with user who has no roles"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        dependency = require_permission("can_read")
        
        # This should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            dependency(current_user=user, db=db_session)
        
        assert exc_info.value.status_code == 403
        assert "does not have required permission: can_read" in str(exc_info.value.detail)


class TestPermissionScenarios:
    """Test various permission scenarios"""
    
    def test_admin_has_all_permissions(self, db_session: Session, setup_roles_and_permissions):
        """Test that Admin role has all permissions"""
        roles = setup_roles_and_permissions["roles"]
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("password123")
        )
        admin_user.roles.append(roles["Admin"])
        db_session.add(admin_user)
        db_session.commit()
        
        # Admin should have all permissions
        assert check_user_permission(admin_user, "can_read") is True
        assert check_user_permission(admin_user, "can_write") is True
        assert check_user_permission(admin_user, "can_delete") is True
    
    def test_editor_has_read_write_permissions(self, db_session: Session, setup_roles_and_permissions):
        """Test that Editor role has read and write permissions only"""
        roles = setup_roles_and_permissions["roles"]
        
        editor_user = User(
            username="editor",
            email="editor@example.com",
            hashed_password=get_password_hash("password123")
        )
        editor_user.roles.append(roles["Editor"])
        db_session.add(editor_user)
        db_session.commit()
        
        # Editor should have read and write, but not delete
        assert check_user_permission(editor_user, "can_read") is True
        assert check_user_permission(editor_user, "can_write") is True
        assert check_user_permission(editor_user, "can_delete") is False
    
    def test_viewer_has_read_permission_only(self, db_session: Session, setup_roles_and_permissions):
        """Test that Viewer role has read permission only"""
        roles = setup_roles_and_permissions["roles"]
        
        viewer_user = User(
            username="viewer",
            email="viewer@example.com",
            hashed_password=get_password_hash("password123")
        )
        viewer_user.roles.append(roles["Viewer"])
        db_session.add(viewer_user)
        db_session.commit()
        
        # Viewer should have read only
        assert check_user_permission(viewer_user, "can_read") is True
        assert check_user_permission(viewer_user, "can_write") is False
        assert check_user_permission(viewer_user, "can_delete") is False
    
    def test_user_with_editor_and_viewer_roles(self, db_session: Session, setup_roles_and_permissions):
        """Test user with both Editor and Viewer roles"""
        roles = setup_roles_and_permissions["roles"]
        
        multi_user = User(
            username="multiuser",
            email="multi@example.com",
            hashed_password=get_password_hash("password123")
        )
        multi_user.roles.extend([roles["Editor"], roles["Viewer"]])
        db_session.add(multi_user)
        db_session.commit()
        
        # Should have combined permissions (read + write from Editor, read from Viewer)
        assert check_user_permission(multi_user, "can_read") is True
        assert check_user_permission(multi_user, "can_write") is True
        assert check_user_permission(multi_user, "can_delete") is False
    
    def test_custom_role_with_specific_permissions(self, db_session: Session, setup_roles_and_permissions):
        """Test custom role with specific permission combination"""
        permissions = setup_roles_and_permissions["permissions"]
        
        # Create custom role with only read and delete permissions
        custom_role = Role(name="CustomRole", description="Custom role for testing")
        custom_role.permissions.extend([
            permissions["can_read"],
            permissions["can_delete"]
        ])
        db_session.add(custom_role)
        db_session.commit()
        
        # Create user with custom role
        custom_user = User(
            username="customuser",
            email="custom@example.com",
            hashed_password=get_password_hash("password123")
        )
        custom_user.roles.append(custom_role)
        db_session.add(custom_user)
        db_session.commit()
        
        # Should have read and delete, but not write
        assert check_user_permission(custom_user, "can_read") is True
        assert check_user_permission(custom_user, "can_write") is False
        assert check_user_permission(custom_user, "can_delete") is True
    
    def test_role_without_permissions(self, db_session: Session):
        """Test role with no permissions assigned"""
        # Create role with no permissions
        empty_role = Role(name="EmptyRole", description="Role with no permissions")
        db_session.add(empty_role)
        db_session.commit()
        
        # Create user with empty role
        user = User(
            username="emptyuser",
            email="empty@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(empty_role)
        db_session.add(user)
        db_session.commit()
        
        # Should have no permissions
        assert check_user_permission(user, "can_read") is False
        assert check_user_permission(user, "can_write") is False
        assert check_user_permission(user, "can_delete") is False
    
    def test_permission_case_sensitivity(self, db_session: Session, setup_roles_and_permissions):
        """Test that permission names are case sensitive"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Admin"])
        db_session.add(user)
        db_session.commit()
        
        # Correct case should work
        assert check_user_permission(user, "can_read") is True
        
        # Wrong case should not work
        assert check_user_permission(user, "CAN_READ") is False
        assert check_user_permission(user, "Can_Read") is False
        assert check_user_permission(user, "can_READ") is False