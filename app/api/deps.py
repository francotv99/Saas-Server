from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    token_data = TokenData(
        user_id=payload.get("user_id"),
        organization_id=payload.get("organization_id"),
        email=payload.get("email")
    )
    
    if token_data.user_id is None:
        raise credentials_exception
    
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(
        token_data.user_id,
        token_data.organization_id
    )
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_organization_id(
    current_user: User = Depends(get_current_user)
) -> int:
    """Dependency to get current user's organization ID."""
    return current_user.organization_id


def require_role(allowed_roles: list[UserRole]):
    """Dependency factory for role-based access control."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return role_checker


# Convenience dependencies
RequireAdmin = Depends(require_role([UserRole.ADMIN]))
RequireMember = Depends(require_role([UserRole.MEMBER, UserRole.ADMIN]))
