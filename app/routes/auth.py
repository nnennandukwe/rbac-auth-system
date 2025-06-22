from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List
from ..models import User, Role
from ..models.base import get_db
from ..auth import create_access_token, verify_password, get_password_hash
from ..logging import get_logger, log_security_event, log_audit_event, SecurityEvents, AuditEvents

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = get_logger("auth")

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return getattr(request.client, "host", "unknown") if request.client else "unknown"

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role_names: List[str] = []

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    
    logger.info(
        f"User registration attempt for username: {user_data.username}",
        extra={"username": user_data.username, "email": user_data.email, "ip_address": client_ip}
    )
    
    try:
        # Check if user exists
        if db.query(User).filter(User.username == user_data.username).first():
            logger.warning(
                f"Registration failed - username already exists: {user_data.username}",
                extra={"username": user_data.username, "ip_address": client_ip, "reason": "username_exists"}
            )
            log_security_event(
                SecurityEvents.REGISTRATION_FAILED,
                f"Registration failed - username already exists: {user_data.username}",
                username=user_data.username,
                ip_address=client_ip,
                additional_data={"reason": "username_exists"}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
            
        if db.query(User).filter(User.email == user_data.email).first():
            logger.warning(
                f"Registration failed - email already exists: {user_data.email}",
                extra={"username": user_data.username, "email": user_data.email, "ip_address": client_ip, "reason": "email_exists"}
            )
            log_security_event(
                SecurityEvents.REGISTRATION_FAILED,
                f"Registration failed - email already exists: {user_data.email}",
                username=user_data.username,
                ip_address=client_ip,
                additional_data={"reason": "email_exists", "email": user_data.email}
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        # Assign roles
        assigned_roles = []
        for role_name in user_data.role_names:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                user.roles.append(role)
                assigned_roles.append(role_name)
            else:
                logger.warning(f"Requested role not found: {role_name}")
        
        # Default to Viewer role if no roles specified
        if not user.roles:
            viewer_role = db.query(Role).filter(Role.name == "Viewer").first()
            if viewer_role:
                user.roles.append(viewer_role)
                assigned_roles.append("Viewer")
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(
            f"User registered successfully: {user.username}",
            extra={
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "roles": assigned_roles,
                "ip_address": client_ip
            }
        )
        
        # Log security and audit events
        log_security_event(
            SecurityEvents.REGISTRATION_SUCCESS,
            f"User registered successfully: {user.username}",
            username=user.username,
            user_id=user.id,
            ip_address=client_ip,
            additional_data={"roles": assigned_roles}
        )
        
        log_audit_event(
            AuditEvents.USER_CREATED,
            f"New user created: {user.username}",
            username=user.username,
            user_id=user.id,
            additional_data={"email": user.email, "roles": assigned_roles}
        )
        
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": [role.name for role in user.roles]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during user registration: {str(e)}",
            extra={"username": user_data.username, "ip_address": client_ip},
            exc_info=True
        )
        log_security_event(
            SecurityEvents.REGISTRATION_FAILED,
            f"Registration failed due to system error: {user_data.username}",
            username=user_data.username,
            ip_address=client_ip,
            additional_data={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request, db: Session = Depends(get_db)):
    client_ip = get_client_ip(request)
    username = form_data.username
    
    logger.info(
        f"Login attempt for username: {username}",
        extra={"username": username, "ip_address": client_ip}
    )
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            logger.warning(
                f"Login failed - user not found: {username}",
                extra={"username": username, "ip_address": client_ip, "reason": "user_not_found"}
            )
            log_security_event(
                SecurityEvents.LOGIN_FAILED,
                f"Login failed - user not found: {username}",
                username=username,
                ip_address=client_ip,
                additional_data={"reason": "user_not_found"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning(
                f"Login failed - invalid password for user: {username}",
                extra={"user_id": user.id, "username": username, "ip_address": client_ip, "reason": "invalid_password"}
            )
            log_security_event(
                SecurityEvents.LOGIN_FAILED,
                f"Login failed - invalid password for user: {username}",
                username=username,
                user_id=user.id,
                ip_address=client_ip,
                additional_data={"reason": "invalid_password"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        user_roles = [role.name for role in user.roles]
        
        logger.info(
            f"Login successful for user: {username}",
            extra={
                "user_id": user.id,
                "username": username,
                "roles": user_roles,
                "ip_address": client_ip,
                "token_expires_minutes": 30
            }
        )
        
        # Log security events
        log_security_event(
            SecurityEvents.LOGIN_SUCCESS,
            f"User logged in successfully: {username}",
            username=username,
            user_id=user.id,
            ip_address=client_ip,
            additional_data={"roles": user_roles}
        )
        
        log_security_event(
            SecurityEvents.TOKEN_CREATED,
            f"Access token created for user: {username}",
            username=username,
            user_id=user.id,
            ip_address=client_ip,
            additional_data={"expires_minutes": 30}
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during login: {str(e)}",
            extra={"username": username, "ip_address": client_ip},
            exc_info=True
        )
        log_security_event(
            SecurityEvents.LOGIN_FAILED,
            f"Login failed due to system error: {username}",
            username=username,
            ip_address=client_ip,
            additional_data={"error": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )