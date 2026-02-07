from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.task import Task, TaskStatus
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository for Task model."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)
    
    async def get_by_status(
        self,
        organization_id: int,
        status: TaskStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by status scoped to organization."""
        query = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.status == status
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_assignee(
        self,
        organization_id: int,
        assignee_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks by assignee scoped to organization."""
        query = select(Task).where(
            and_(
                Task.organization_id == organization_id,
                Task.assignee_id == assignee_id
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
