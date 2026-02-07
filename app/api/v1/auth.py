from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.auth import UserLogin, UserRegister, Token
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user and organization."""
    auth_service = AuthService(db)
    try:
        user, access_token = await auth_service.register_user(data)
        return Token(access_token=access_token, token_type="bearer")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(
        credentials.email,
        credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token_for_user(user)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return current_user
