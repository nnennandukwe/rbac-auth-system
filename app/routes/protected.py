from fastapi import APIRouter, Depends
from ..models import User
from ..permissions import require_permission
from ..logging import get_logger, log_audit_event, AuditEvents

router = APIRouter(tags=["protected"])
logger = get_logger("protected")

@router.get("/admin")
def admin_route(current_user: User = Depends(require_permission("can_delete"))):
    logger.info(
        f"Admin area accessed by user: {current_user.username}",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "endpoint": "/admin",
            "roles": [role.name for role in current_user.roles]
        }
    )
    
    log_audit_event(
        AuditEvents.API_ACCESS,
        f"Admin area accessed by user: {current_user.username}",
        username=current_user.username,
        user_id=current_user.id,
        resource="/admin",
        additional_data={"roles": [role.name for role in current_user.roles]}
    )
    
    return {
        "message": "Welcome to admin area",
        "user": current_user.username,
        "roles": [role.name for role in current_user.roles]
    }

@router.get("/edit")
def edit_route(current_user: User = Depends(require_permission("can_write"))):
    logger.info(
        f"Editor area accessed by user: {current_user.username}",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "endpoint": "/edit",
            "roles": [role.name for role in current_user.roles]
        }
    )
    
    log_audit_event(
        AuditEvents.API_ACCESS,
        f"Editor area accessed by user: {current_user.username}",
        username=current_user.username,
        user_id=current_user.id,
        resource="/edit",
        additional_data={"roles": [role.name for role in current_user.roles]}
    )
    
    return {
        "message": "Welcome to editor area",
        "user": current_user.username,
        "roles": [role.name for role in current_user.roles]
    }

@router.get("/view")
def view_route(current_user: User = Depends(require_permission("can_read"))):
    logger.info(
        f"Viewer area accessed by user: {current_user.username}",
        extra={
            "user_id": current_user.id,
            "username": current_user.username,
            "endpoint": "/view",
            "roles": [role.name for role in current_user.roles]
        }
    )
    
    log_audit_event(
        AuditEvents.API_ACCESS,
        f"Viewer area accessed by user: {current_user.username}",
        username=current_user.username,
        user_id=current_user.id,
        resource="/view",
        additional_data={"roles": [role.name for role in current_user.roles]}
    )
    
    return {
        "message": "Welcome to viewer area",
        "user": current_user.username,
        "roles": [role.name for role in current_user.roles]
    }