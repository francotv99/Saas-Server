from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Organization, db)
    
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        query = select(Organization).where(Organization.slug == slug)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(self, name: str, slug: str) -> Organization:
        """Create a new organization."""
        org = Organization(name=name, slug=slug)
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)
        return org
