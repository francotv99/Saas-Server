from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrganizationUpdate


class OrganizationService:
    """Service for organization operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.org_repo = OrganizationRepository(db)
    
    async def get_organization(
        self,
        organization_id: int
    ) -> Optional[Organization]:
        """Get organization by ID."""
        return await self.org_repo.get_by_id(organization_id, organization_id)
    
    async def update_organization(
        self,
        organization_id: int,
        data: OrganizationUpdate
    ) -> Optional[Organization]:
        """Update organization."""
        update_data = data.dict(exclude_unset=True)
        
        # Check slug uniqueness if updating slug
        if "slug" in update_data:
            existing = await self.org_repo.get_by_slug(update_data["slug"])
            if existing and existing.id != organization_id:
                raise ValueError(f"Organization with slug '{update_data['slug']}' already exists")
        
        return await self.org_repo.update(organization_id, organization_id, update_data)
