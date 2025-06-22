from passlib.context import CryptContext
from ..logging import get_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = get_logger("auth.password")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification {'successful' if result else 'failed'}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    """Generate a hash for a plain password"""
    try:
        hashed = pwd_context.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}", exc_info=True)
        raise