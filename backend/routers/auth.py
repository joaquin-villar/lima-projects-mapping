from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
import jwt
import os

router = APIRouter()

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    
    try:
        token = authorization.replace("Bearer ", "")
        # Verify with Neon Auth public key
        payload = jwt.decode(
            token, 
            os.getenv("NEXT_PUBLIC_STACK_PUBLISHABLE_CLIENT_KEY"),
            algorithms=["RS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Protect your routes
@router.get("/protected")
def protected_route(user = Depends(verify_token)):
    return {"user_id": user["sub"], "message": "Access granted"}