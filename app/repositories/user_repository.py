from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email (no tenant scoping for auth purposes)."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email_and_org(
        self,
        email: str,
        organization_id: int
    ) -> Optional[User]:
        """Get user by email scoped to organization."""
        query = select(User).where(
            User.email == email,
            User.organization_id == organization_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
