"""
Tests for authentication utilities (JWT, password hashing, etc.).
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.password import verify_password, get_password_hash
from app.auth.jwt import create_access_token, get_current_user
from app.models import User
from app.auth import get_password_hash as auth_get_password_hash


class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Hash should be a string
        assert isinstance(hashed, str)
        
        # Hash should have reasonable length (bcrypt hashes are typically 60 chars)
        assert len(hashed) > 50
    
    def test_password_verification_success(self):
        """Test successful password verification"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Verification should succeed with correct password
        assert verify_password(password, hashed) is True
    
    def test_password_verification_failure(self):
        """Test failed password verification"""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = get_password_hash(password)
        
        # Verification should fail with wrong password
        assert verify_password(wrong_password, hashed) is False
    
    def test_password_hashing_consistency(self):
        """Test that same password produces different hashes (salt)"""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True
    
    def test_empty_password_handling(self):
        """Test handling of empty passwords"""
        empty_password = ""
        hashed = get_password_hash(empty_password)
        
        # Should still produce a hash
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        
        # Should verify correctly
        assert verify_password(empty_password, hashed) is True
    
    def test_special_characters_in_password(self):
        """Test passwords with special characters"""
        special_password = "p@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
        hashed = get_password_hash(special_password)
        
        assert verify_password(special_password, hashed) is True
    
    def test_unicode_password(self):
        """Test passwords with unicode characters"""
        unicode_password = "пароль123密码"
        hashed = get_password_hash(unicode_password)
        
        assert verify_password(unicode_password, hashed) is True


class TestJWTTokens:
    """Test JWT token creation and validation"""
    
    def test_create_access_token(self):
        """Test creating access tokens"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Token should have reasonable length
        assert len(token) > 50
        
        # Token should be decodable
        from app.auth.jwt import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "testuser"
    
    def test_create_access_token_with_expiration(self):
        """Test creating access tokens with custom expiration"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        # Decode and check expiration
        from app.auth.jwt import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Should have expiration claim
        assert "exp" in decoded
        
        # Expiration should be approximately 15 minutes from now
        exp_time = datetime.fromtimestamp(decoded["exp"])
        expected_time = datetime.utcnow() + expires_delta
        
        # Allow 1 minute tolerance for test execution time
        assert abs((exp_time - expected_time).total_seconds()) < 60
    
    def test_create_access_token_default_expiration(self):
        """Test that tokens have default expiration when none specified"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        from app.auth.jwt import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Should have expiration claim
        assert "exp" in decoded
        
        # Should expire in the future
        exp_time = datetime.fromtimestamp(decoded["exp"])
        assert exp_time > datetime.utcnow()
    
    def test_token_with_additional_claims(self):
        """Test creating tokens with additional claims"""
        data = {
            "sub": "testuser",
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }
        token = create_access_token(data)
        
        from app.auth.jwt import SECRET_KEY, ALGORITHM
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
        assert decoded["permissions"] == ["read", "write", "delete"]


class TestGetCurrentUser:
    """Test get_current_user dependency"""
    
    def test_get_current_user_with_valid_token(self, db_session: Session, setup_roles_and_permissions):
        """Test getting current user with valid token"""
        roles = setup_roles_and_permissions["roles"]
        
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Admin"])
        db_session.add(user)
        db_session.commit()
        
        # Create token
        token = create_access_token({"sub": "testuser"})
        
        # Get current user
        current_user = get_current_user(token, db_session)
        
        assert current_user.username == "testuser"
        assert current_user.email == "test@example.com"
        assert len(current_user.roles) == 1
        assert current_user.roles[0].name == "Admin"
    
    def test_get_current_user_with_invalid_token(self, db_session: Session):
        """Test getting current user with invalid token raises exception"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(invalid_token, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_get_current_user_with_expired_token(self, db_session: Session, setup_roles_and_permissions):
        """Test getting current user with expired token raises exception"""
        roles = setup_roles_and_permissions["roles"]
        
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123")
        )
        user.roles.append(roles["Admin"])
        db_session.add(user)
        db_session.commit()
        
        # Create expired token (expired 1 minute ago)
        expired_delta = timedelta(minutes=-1)
        expired_token = create_access_token({"sub": "testuser"}, expired_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(expired_token, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_get_current_user_with_nonexistent_user(self, db_session: Session):
        """Test getting current user for non-existent user raises exception"""
        # Create token for user that doesn't exist in database
        token = create_access_token({"sub": "nonexistent_user"})
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_get_current_user_with_malformed_token(self, db_session: Session):
        """Test getting current user with malformed token raises exception"""
        malformed_tokens = [
            "not.a.jwt",
            "too.few.parts",
            "too.many.parts.in.this.token",
            "",
            "Bearer token_here",  # Should not include Bearer prefix
        ]
        
        for malformed_token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(malformed_token, db_session)
            
            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)
    
    def test_get_current_user_with_token_missing_subject(self, db_session: Session):
        """Test getting current user with token missing subject claim"""
        # Create token without 'sub' claim
        token = create_access_token({"user": "testuser"})  # Wrong claim name
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token, db_session)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)


class TestAuthUtilsIntegration:
    """Test integration between different auth utilities"""
    
    def test_complete_auth_flow(self, db_session: Session, setup_roles_and_permissions):
        """Test complete authentication flow"""
        roles = setup_roles_and_permissions["roles"]
        
        # 1. Hash password
        plain_password = "secure_password_123"
        hashed_password = get_password_hash(plain_password)
        
        # 2. Create user with hashed password
        user = User(
            username="auth_flow_user",
            email="authflow@example.com",
            hashed_password=hashed_password
        )
        user.roles.append(roles["Editor"])
        db_session.add(user)
        db_session.commit()
        
        # 3. Verify password (simulating login)
        assert verify_password(plain_password, user.hashed_password) is True
        
        # 4. Create access token
        token = create_access_token({"sub": user.username})
        
        # 5. Get current user from token
        current_user = get_current_user(token, db_session)
        
        # 6. Verify we got the right user
        assert current_user.id == user.id
        assert current_user.username == user.username
        assert current_user.email == user.email
        assert len(current_user.roles) == 1
        assert current_user.roles[0].name == "Editor"
    
    def test_password_change_scenario(self, db_session: Session, setup_roles_and_permissions):
        """Test scenario where user changes password"""
        roles = setup_roles_and_permissions["roles"]
        
        # Create user with initial password
        old_password = "old_password_123"
        user = User(
            username="password_change_user",
            email="pwchange@example.com",
            hashed_password=get_password_hash(old_password)
        )
        user.roles.append(roles["Viewer"])
        db_session.add(user)
        db_session.commit()
        
        # Verify old password works
        assert verify_password(old_password, user.hashed_password) is True
        
        # Change password
        new_password = "new_password_456"
        user.hashed_password = get_password_hash(new_password)
        db_session.commit()
        
        # Old password should no longer work
        assert verify_password(old_password, user.hashed_password) is False
        
        # New password should work
        assert verify_password(new_password, user.hashed_password) is True
        
        # Token creation should still work with user
        token = create_access_token({"sub": user.username})
        current_user = get_current_user(token, db_session)
        assert current_user.id == user.id
    
    def test_token_security_properties(self):
        """Test security properties of generated tokens"""
        # Create multiple tokens for same user
        data = {"sub": "testuser"}
        token1 = create_access_token(data)
        token2 = create_access_token(data)
        
        # Tokens should be different (due to timestamp and potentially other factors)
        assert token1 != token2
        
        # But both should decode to same user
        from app.auth.jwt import SECRET_KEY, ALGORITHM
        decoded1 = jwt.decode(token1, SECRET_KEY, algorithms=[ALGORITHM])
        decoded2 = jwt.decode(token2, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert decoded1["sub"] == decoded2["sub"] == "testuser"
    
    def test_auth_utils_import_consistency(self):
        """Test that auth utilities can be imported from different locations"""
        # Test that password hashing functions are consistent
        from app.auth.password import get_password_hash as pwd_hash
        from app.auth import get_password_hash as auth_hash
        
        password = "test_password"
        hash1 = pwd_hash(password)
        hash2 = auth_hash(password)
        
        # Both should produce valid hashes
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True