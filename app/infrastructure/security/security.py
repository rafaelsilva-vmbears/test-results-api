import os
from fastapi import Header, HTTPException, status, Request
from dotenv import load_dotenv
from app.infrastructure.repositories.mongo_api_key_repository import MongoApiKeyRepository

load_dotenv()

API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-Key")
MASTER_KEY = os.getenv("MASTER_KEY")  # New Master Key for admin actions

# Fallback for backward compatibility or initial setup
LEGACY_API_KEY = os.getenv("API_KEY")

from app.domain.entities.permission_enum import Permission

def verify_read_permission(request: Request, x_api_key: str = Header(None, alias=API_KEY_NAME)):
    """Verifies if the API Key has READ permission."""
    return _verify_permission(request, x_api_key, Permission.READ)

def verify_write_permission(request: Request, x_api_key: str = Header(None, alias=API_KEY_NAME)):
    """Verifies if the API Key has WRITE permission."""
    return _verify_permission(request, x_api_key, Permission.WRITE)

def _verify_permission(request: Request, x_api_key: str, required_permission: Permission):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid API Key required."
        )

    # 1. Master Key check (Admin access / All permissions)
    if MASTER_KEY and x_api_key == MASTER_KEY:
        return True

    # 2. Legacy Env Key check (Backward compatibility - Implies Full Access)
    if LEGACY_API_KEY and x_api_key == LEGACY_API_KEY:
        return True

    # 3. MongoDB check
    try:
        adapter = request.app.state.db_adapter
        repo = MongoApiKeyRepository(adapter)
        api_key_entity = repo.get_by_key(x_api_key)

        if api_key_entity and api_key_entity.is_active:
            # Check for specific permission or ADMIN
            if (required_permission in api_key_entity.permissions) or (Permission.ADMIN in api_key_entity.permissions):
                return True

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_permission}"
            )

    except HTTPException:
        raise
    except Exception as e:
        # Log error?
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or revoked API Key."
    )

def verify_api_key(request: Request, x_api_key: str = Header(None, alias=API_KEY_NAME)):
    """
    Deprecated: Use verify_read_permission or verify_write_permission instead.
    Maintained for generic checks if needed.
    """
    return _verify_permission(request, x_api_key, Permission.READ) # Default to checking at least READ? Or just authentication?

def verify_master_key(x_api_key: str = Header(None, alias=API_KEY_NAME)):
    """
    Dependency to ensure exclusively Master Key access.
    """
    if not MASTER_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Master Key not configured."
        )

    if x_api_key != MASTER_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required."
        )
    return True
