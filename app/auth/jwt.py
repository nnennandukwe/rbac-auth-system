from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..models.base import get_db
from ..models import User
from ..logging import get_logger, log_security_event, SecurityEvents

SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
logger = get_logger("auth.jwt")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.debug(
            f"Access token created for subject: {data.get('sub', 'unknown')}",
            extra={
                "subject": data.get("sub"),
                "expires_at": expire.isoformat(),
                "algorithm": ALGORITHM
            }
        )
        
        return encoded_jwt
        
    except Exception as e:
        logger.error(
            f"Failed to create access token: {str(e)}",
            extra={"subject": data.get("sub")},
            exc_info=True
        )
        raise

def verify_token(token: str, credentials_exception):
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            logger.warning("Token validation failed - no subject in token")
            log_security_event(
                SecurityEvents.TOKEN_VALIDATION_FAILED,
                "Token validation failed - no subject in token",
                additional_data={"reason": "no_subject"}
            )
            raise credentials_exception
            
        logger.debug(
            f"Token validated successfully for user: {username}",
            extra={"username": username}
        )
        
        return username
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token validation failed - token expired")
        log_security_event(
            SecurityEvents.TOKEN_VALIDATION_FAILED,
            "Token validation failed - token expired",
            additional_data={"reason": "expired"}
        )
        raise credentials_exception
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token validation failed - invalid token: {str(e)}")
        log_security_event(
            SecurityEvents.TOKEN_VALIDATION_FAILED,
            f"Token validation failed - invalid token: {str(e)}",
            additional_data={"reason": "invalid_token", "error": str(e)}
        )
        raise credentials_exception
    except JWTError as e:
        logger.warning(f"Token validation failed - JWT error: {str(e)}")
        log_security_event(
            SecurityEvents.TOKEN_VALIDATION_FAILED,
            f"Token validation failed - JWT error: {str(e)}",
            additional_data={"reason": "jwt_error", "error": str(e)}
        )
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        username = verify_token(token, credentials_exception)
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            logger.warning(
                f"User not found in database: {username}",
                extra={"username": username}
            )
            log_security_event(
                SecurityEvents.TOKEN_VALIDATION_FAILED,
                f"Token validation failed - user not found: {username}",
                username=username,
                additional_data={"reason": "user_not_found"}
            )
            raise credentials_exception
            
        logger.debug(
            f"Current user retrieved successfully: {username}",
            extra={
                "user_id": user.id,
                "username": username,
                "roles": [role.name for role in user.roles]
            }
        )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error getting current user: {str(e)}",
            exc_info=True
        )
        raise credentials_exception