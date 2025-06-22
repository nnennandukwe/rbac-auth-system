from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..models import User
from ..models.base import get_db
from ..auth import get_current_user
from ..logging import get_logger, log_security_event, log_audit_event, SecurityEvents, AuditEvents

logger = get_logger("permissions")

def check_user_permission(user: User, permission_name: str) -> bool:
    """
    Check if user has the required permission.
    Fixed the bug: Now properly checks for the specific permission
    """
    logger.debug(
        f"Checking permission '{permission_name}' for user: {user.username}",
        extra={
            "user_id": user.id,
            "username": user.username,
            "permission": permission_name,
            "user_roles": [role.name for role in user.roles]
        }
    )
    
    for role in user.roles:
        for permission in role.permissions:
            # FIXED: Now properly checks if the permission name matches
            if permission.name == permission_name:
                logger.debug(
                    f"Permission '{permission_name}' granted to user {user.username} via role {role.name}",
                    extra={
                        "user_id": user.id,
                        "username": user.username,
                        "permission": permission_name,
                        "role": role.name
                    }
                )
                return True
    
    logger.warning(
        f"Permission '{permission_name}' denied for user: {user.username}",
        extra={
            "user_id": user.id,
            "username": user.username,
            "permission": permission_name,
            "user_roles": [role.name for role in user.roles]
        }
    )
    
    return False

def require_permission(permission_name: str):
    """Dependency factory that creates a permission check dependency"""
    def permission_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        logger.info(
            f"Permission check requested: {permission_name} for user: {current_user.username}",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "permission": permission_name
            }
        )
        
        # Log audit event for permission check
        log_audit_event(
            AuditEvents.PERMISSION_CHECK,
            f"Permission check: {permission_name} for user {current_user.username}",
            username=current_user.username,
            user_id=current_user.id,
            additional_data={"permission": permission_name}
        )
        
        if not check_user_permission(current_user, permission_name):
            # Log security event for permission denial
            log_security_event(
                SecurityEvents.PERMISSION_DENIED,
                f"Permission denied: {permission_name} for user {current_user.username}",
                username=current_user.username,
                user_id=current_user.id,
                additional_data={
                    "permission": permission_name,
                    "roles": [role.name for role in current_user.roles]
                }
            )
            
            logger.error(
                f"Access denied - insufficient permissions for user: {current_user.username}",
                extra={
                    "user_id": current_user.id,
                    "username": current_user.username,
                    "permission": permission_name,
                    "user_roles": [role.name for role in current_user.roles]
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have required permission: {permission_name}"
            )
        
        # Log successful permission grant
        log_security_event(
            SecurityEvents.PERMISSION_GRANTED,
            f"Permission granted: {permission_name} for user {current_user.username}",
            username=current_user.username,
            user_id=current_user.id,
            additional_data={
                "permission": permission_name,
                "roles": [role.name for role in current_user.roles]
            }
        )
        
        logger.info(
            f"Access granted - user {current_user.username} has permission: {permission_name}",
            extra={
                "user_id": current_user.id,
                "username": current_user.username,
                "permission": permission_name
            }
        )
        
        return current_user
    return permission_dependency