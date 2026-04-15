from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
try:
    from fastapi.security import HTTPAuthorizationCredentials
except ImportError:
    # Fallback for different fastapi versions
    from fastapi.security.http import HTTPAuthorizationCredentials

from app.utils.auth import decode_access_token
from app.models.database import get_users_collection
from bson import ObjectId

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Verify user exists
        users_col = get_users_collection()
        user = await users_col.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
