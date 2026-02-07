from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.schemas.auth import UserLogin, UserRegister, TokenData
from app.config import settings


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.org_repo = OrganizationRepository(db)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    async def register_user(self, data: UserRegister) -> tuple[User, str]:
        """Register a new user and organization."""
        # Check if organization slug already exists
        existing_org = await self.org_repo.get_by_slug(data.organization_slug)
        if existing_org:
            raise ValueError(f"Organization with slug '{data.organization_slug}' already exists")
        
        # Check if user email already exists
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise ValueError(f"User with email '{data.email}' already exists")
        
        # Create organization
        organization = await self.org_repo.create(
            name=data.organization_name,
            slug=data.organization_slug
        )
        
        # Create user (as admin of the new organization)
        hashed_password = get_password_hash(data.password)
        user = User(
            email=data.email,
            hashed_password=hashed_password,
            full_name=data.full_name,
            role=UserRole.ADMIN,
            organization_id=organization.id
        )
        
        user = await self.user_repo.create(user)
        
        # Generate token
        token_data = TokenData(
            user_id=user.id,
            organization_id=user.organization_id,
            email=user.email
        )
        access_token = create_access_token(token_data.dict())
        
        return user, access_token
    
    def create_access_token_for_user(self, user: User) -> str:
        """Create an access token for a user."""
        token_data = TokenData(
            user_id=user.id,
            organization_id=user.organization_id,
            email=user.email
        )
        return create_access_token(token_data.dict())
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate a JWT token."""
        payload = decode_access_token(token)
        if not payload:
            return None
        
        return TokenData(
            user_id=payload.get("user_id"),
            organization_id=payload.get("organization_id"),
            email=payload.get("email")
        )
