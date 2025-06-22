"""
Tests for database models and their relationships.
"""

import pytest
from sqlalchemy.orm import Session
from app.models import User, Role, Permission
from app.auth import get_password_hash


class TestUserModel:
    """Test User model functionality"""
    
    def test_create_user(self, db_session: Session):
        """Test creating a user"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert user.hashed_password != "password123"  # Should be hashed
    
    def test_user_unique_username(self, db_session: Session):
        """Test that usernames must be unique"""
        user1 = User(
            username="testuser",
            email="test1@example.com",
            hashed_password=get_password_hash("password123")
        )
        user2 = User(
            username="testuser",  # Same username
            email="test2@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_unique_email(self, db_session: Session):
        """Test that emails must be unique"""
        user1 = User(
            username="testuser1",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user2 = User(
            username="testuser2",
            email="test@example.com",  # Same email
            hashed_password=get_password_hash("password123")
        )
        
        db_session.add(user1)
        db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_user_has_permission_method(self, db_session: Session, setup_roles_and_permissions):
        """Test User.has_permission method"""
        roles = setup_roles_and_permissions["roles"]
        
        # Create user with Admin role
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("password123")
        )
        admin_user.roles.append(roles["Admin"])
        db_session.add(admin_user)
        db_session.commit()
        
        # Test permissions
        assert admin_user.has_permission("can_read") is True
        assert admin_user.has_permission("can_write") is True
        assert admin_user.has_permission("can_delete") is True
        assert admin_user.has_permission("nonexistent_permission") is False
    
    def test_user_multiple_roles(self, db_session: Session, setup_roles_and_permissions):
        """Test user with multiple roles"""
        roles = setup_roles_and_permissions["roles"]
        
        user = User(
            username="multiuser",
            email="multi@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.extend([roles["Editor"], roles["Viewer"]])
        db_session.add(user)
        db_session.commit()
        
        assert len(user.roles) == 2
        assert roles["Editor"] in user.roles
        assert roles["Viewer"] in user.roles
        
        # Should have permissions from both roles
        assert user.has_permission("can_read") is True
        assert user.has_permission("can_write") is True
        assert user.has_permission("can_delete") is False


class TestRoleModel:
    """Test Role model functionality"""
    
    def test_create_role(self, db_session: Session):
        """Test creating a role"""
        role = Role(
            name="TestRole",
            description="A test role"
        )
        db_session.add(role)
        db_session.commit()
        
        assert role.id is not None
        assert role.name == "TestRole"
        assert role.description == "A test role"
    
    def test_role_unique_name(self, db_session: Session):
        """Test that role names must be unique"""
        role1 = Role(name="TestRole", description="First role")
        role2 = Role(name="TestRole", description="Second role")
        
        db_session.add(role1)
        db_session.commit()
        
        db_session.add(role2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_role_permissions_relationship(self, db_session: Session):
        """Test role-permissions relationship"""
        # Create permissions
        perm1 = Permission(name="test_perm1", description="Test permission 1")
        perm2 = Permission(name="test_perm2", description="Test permission 2")
        db_session.add_all([perm1, perm2])
        db_session.commit()
        
        # Create role with permissions
        role = Role(name="TestRole", description="Test role")
        role.permissions.extend([perm1, perm2])
        db_session.add(role)
        db_session.commit()
        
        assert len(role.permissions) == 2
        assert perm1 in role.permissions
        assert perm2 in role.permissions
    
    def test_role_users_relationship(self, db_session: Session):
        """Test role-users relationship"""
        # Create role
        role = Role(name="TestRole", description="Test role")
        db_session.add(role)
        db_session.commit()
        
        # Create users
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=get_password_hash("password123")
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=get_password_hash("password123")
        )
        
        # Assign role to users
        user1.roles.append(role)
        user2.roles.append(role)
        db_session.add_all([user1, user2])
        db_session.commit()
        
        assert len(role.users) == 2
        assert user1 in role.users
        assert user2 in role.users


class TestPermissionModel:
    """Test Permission model functionality"""
    
    def test_create_permission(self, db_session: Session):
        """Test creating a permission"""
        permission = Permission(
            name="test_permission",
            description="A test permission"
        )
        db_session.add(permission)
        db_session.commit()
        
        assert permission.id is not None
        assert permission.name == "test_permission"
        assert permission.description == "A test permission"
    
    def test_permission_unique_name(self, db_session: Session):
        """Test that permission names must be unique"""
        perm1 = Permission(name="test_perm", description="First permission")
        perm2 = Permission(name="test_perm", description="Second permission")
        
        db_session.add(perm1)
        db_session.commit()
        
        db_session.add(perm2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_permission_roles_relationship(self, db_session: Session):
        """Test permission-roles relationship"""
        # Create permission
        permission = Permission(name="test_perm", description="Test permission")
        db_session.add(permission)
        db_session.commit()
        
        # Create roles
        role1 = Role(name="Role1", description="First role")
        role2 = Role(name="Role2", description="Second role")
        
        # Assign permission to roles
        role1.permissions.append(permission)
        role2.permissions.append(permission)
        db_session.add_all([role1, role2])
        db_session.commit()
        
        assert len(permission.roles) == 2
        assert role1 in permission.roles
        assert role2 in permission.roles


class TestModelRelationships:
    """Test complex model relationships"""
    
    def test_user_role_permission_chain(self, db_session: Session):
        """Test the complete user -> role -> permission chain"""
        # Create permission
        permission = Permission(name="test_perm", description="Test permission")
        db_session.add(permission)
        db_session.commit()
        
        # Create role with permission
        role = Role(name="TestRole", description="Test role")
        role.permissions.append(permission)
        db_session.add(role)
        db_session.commit()
        
        # Create user with role
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(role)
        db_session.add(user)
        db_session.commit()
        
        # Test the chain
        assert len(user.roles) == 1
        assert user.roles[0] == role
        assert len(user.roles[0].permissions) == 1
        assert user.roles[0].permissions[0] == permission
        assert user.has_permission("test_perm") is True
    
    def test_many_to_many_relationships(self, db_session: Session):
        """Test many-to-many relationships work correctly"""
        # Create permissions
        perm1 = Permission(name="perm1", description="Permission 1")
        perm2 = Permission(name="perm2", description="Permission 2")
        perm3 = Permission(name="perm3", description="Permission 3")
        db_session.add_all([perm1, perm2, perm3])
        db_session.commit()
        
        # Create roles with different permission combinations
        role1 = Role(name="Role1", description="Role 1")
        role1.permissions.extend([perm1, perm2])
        
        role2 = Role(name="Role2", description="Role 2")
        role2.permissions.extend([perm2, perm3])
        
        db_session.add_all([role1, role2])
        db_session.commit()
        
        # Create users with different role combinations
        user1 = User(
            username="user1",
            email="user1@example.com",
            hashed_password=get_password_hash("password123")
        )
        user1.roles.append(role1)
        
        user2 = User(
            username="user2",
            email="user2@example.com",
            hashed_password=get_password_hash("password123")
        )
        user2.roles.extend([role1, role2])
        
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Test user1 permissions (only role1)
        assert user1.has_permission("perm1") is True
        assert user1.has_permission("perm2") is True
        assert user1.has_permission("perm3") is False
        
        # Test user2 permissions (role1 + role2)
        assert user2.has_permission("perm1") is True
        assert user2.has_permission("perm2") is True
        assert user2.has_permission("perm3") is True
    
    def test_cascade_relationships(self, db_session: Session):
        """Test that relationships are properly maintained"""
        # Create a complete setup
        permission = Permission(name="test_perm", description="Test permission")
        role = Role(name="TestRole", description="Test role")
        role.permissions.append(permission)
        
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(role)
        
        db_session.add_all([permission, role, user])
        db_session.commit()
        
        # Verify all relationships exist
        assert len(user.roles) == 1
        assert len(role.users) == 1
        assert len(role.permissions) == 1
        assert len(permission.roles) == 1
        
        # Test that we can navigate the relationships
        assert user.roles[0].permissions[0] == permission
        assert permission.roles[0].users[0] == user