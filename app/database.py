from sqlalchemy.orm import Session
from .models import User, Role, Permission
from .models.base import Base, engine, SessionLocal
from .auth import get_password_hash
from .logging import get_logger, log_audit_event, AuditEvents

logger = get_logger("database")

def init_db():
    """Initialize database with tables and seed data"""
    logger.info("Starting database initialization")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        db = SessionLocal()
        
        # Check if already seeded
        role_count = db.query(Role).count()
        if role_count > 0:
            logger.info(f"Database already seeded with {role_count} roles, skipping seed data")
            db.close()
            return
        
        logger.info("Seeding database with initial data")
        
        # Create permissions
        permissions = {
            "can_read": Permission(name="can_read", description="Can read resources"),
            "can_write": Permission(name="can_write", description="Can write resources"),
            "can_delete": Permission(name="can_delete", description="Can delete resources")
        }
        
        for perm_name, perm in permissions.items():
            db.add(perm)
            logger.debug(f"Created permission: {perm_name}")
        
        # Create roles
        admin_role = Role(name="Admin", description="Administrator with full access")
        admin_role.permissions.extend(permissions.values())
        
        editor_role = Role(name="Editor", description="Can read and write")
        editor_role.permissions.extend([permissions["can_read"], permissions["can_write"]])
        
        viewer_role = Role(name="Viewer", description="Can only read")
        viewer_role.permissions.append(permissions["can_read"])
        
        db.add(admin_role)
        db.add(editor_role)
        db.add(viewer_role)
        
        logger.info("Created roles: Admin, Editor, Viewer")
        
        # Create a test admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123")
        )
        admin_user.roles.append(admin_role)
        db.add(admin_user)
        
        logger.info("Created default admin user")
        
        # Commit all changes
        db.commit()
        db.close()
        
        logger.info("Database initialization completed successfully")
        
        # Log audit event
        log_audit_event(
            AuditEvents.DATABASE_INITIALIZED,
            "Database initialized with seed data",
            additional_data={
                "permissions_created": len(permissions),
                "roles_created": 3,
                "users_created": 1
            }
        )
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        raise