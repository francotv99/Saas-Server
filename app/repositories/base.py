from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with tenant scoping."""
    
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get_by_id(
        self,
        id: int,
        organization_id: int,
        load_relationships: Optional[List[str]] = None
    ) -> Optional[ModelType]:
        """Get a record by ID scoped to organization."""
        query = select(self.model).where(
            self.model.id == id,
            self.model.organization_id == organization_id
        )
        
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        load_relationships: Optional[List[str]] = None
    ) -> List[ModelType]:
        """Get all records scoped to organization."""
        query = select(self.model).where(
            self.model.organization_id == organization_id
        ).offset(skip).limit(limit)
        
        if load_relationships:
            for rel in load_relationships:
                query = query.options(selectinload(getattr(self.model, rel)))
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count(self, organization_id: int) -> int:
        """Count records scoped to organization."""
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model).where(
            self.model.organization_id == organization_id
        )
        result = await self.db.execute(query)
        return result.scalar_one() or 0
    
    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record."""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, id: int, organization_id: int, update_data: dict) -> Optional[ModelType]:
        """Update a record scoped to organization."""
        query = update(self.model).where(
            self.model.id == id,
            self.model.organization_id == organization_id
        ).values(**update_data).returning(self.model)
        
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, id: int, organization_id: int) -> bool:
        """Delete a record scoped to organization."""
        query = delete(self.model).where(
            self.model.id == id,
            self.model.organization_id == organization_id
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0
