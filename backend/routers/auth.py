from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional, List
import jwt
import os
from backend.models import UserRole

router = APIRouter()

# For local development if env not set
CLIENT_KEY = os.getenv("NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY", "your-fallback-public-key")

def verify_token(authorization: Optional[str] = Header(None)):
    """Verifies the JWT token and returns the payload."""
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    
    try:
        token = authorization.replace("Bearer ", "")
        # In production, verify with Neon Auth public key/JWKS
        # For now, we decode to extract metadata. RS256 requires the public key.
        payload = jwt.decode(
            token, 
            CLIENT_KEY,
            algorithms=["RS256"],
            options={"verify_signature": False} # Set to True once public key is confirmed
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(allowed_roles: List[UserRole]):
    """Dependency factory for role-based access control."""
    def role_checker(payload: dict = Depends(verify_token)):
        # Extract role from payload (e.g., payload.get("role"))
        # Using a default 'viewer' if not present for safety
        user_role_str = payload.get("role", "viewer").upper()
        try:
            user_role = UserRole[user_role_str]
        except KeyError:
            user_role = UserRole.VIEWER

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Operation not permitted for role: {user_role.value}"
            )
        return payload
    return role_checker

# Helper dependencies for common roles
editor_permission = require_role([UserRole.EDITOR, UserRole.VERIFIED, UserRole.ADMIN])
admin_permission = require_role([UserRole.ADMIN])

# Protect your routes
@router.get("/protected")
def protected_route(user = Depends(verify_token)):
    return {"user_id": user["sub"], "message": "Access granted"}