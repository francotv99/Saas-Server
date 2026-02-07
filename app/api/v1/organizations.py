from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import (
    get_current_user,
    get_current_organization_id,
    RequireAdmin,
    RequireMember
)
from app.models.user import User
from app.schemas.organization import OrganizationResponse, OrganizationUpdate
from app.services.organization_service import OrganizationService

router = APIRouter()


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = RequireMember,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's organization."""
    org_service = OrganizationService(db)
    org = await org_service.get_organization(organization_id)
    
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return org


@router.patch("/me", response_model=OrganizationResponse)
async def update_my_organization(
    data: OrganizationUpdate,
    current_user: User = RequireAdmin,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's organization (admin only)."""
    org_service = OrganizationService(db)
    try:
        org = await org_service.update_organization(organization_id, data)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )
        return org
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
