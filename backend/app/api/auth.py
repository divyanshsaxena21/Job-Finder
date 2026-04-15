from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.utils.auth import create_access_token
from app.utils.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        user = await AuthService.register(user_data)
        
        token = create_access_token(str(user["_id"]), user["email"])
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                _id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                telegram_chat_id=user.get("telegram_chat_id"),
                created_at=user["created_at"]
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    try:
        user = await AuthService.login(credentials.email, credentials.password)
        
        token = create_access_token(str(user["_id"]), user["email"])
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                _id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                telegram_chat_id=user.get("telegram_chat_id"),
                created_at=user["created_at"]
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(
        _id=str(current_user["_id"]),
        name=current_user["name"],
        email=current_user["email"],
        telegram_chat_id=current_user.get("telegram_chat_id"),
        created_at=current_user["created_at"]
    )
