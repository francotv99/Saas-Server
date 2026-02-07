from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.utils.pagination import PaginationParams, PaginatedResponse
from app.workers.tasks import send_task_created_notification


class TaskService:
    """Service for task operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.user_repo = UserRepository(db)
    
    async def create_task(
        self,
        organization_id: int,
        data: TaskCreate,
        created_by_user_id: int
    ) -> Task:
        """Create a new task."""
        # Verify assignee belongs to the same organization if provided
        if data.assignee_id:
            assignee = await self.user_repo.get_by_id(
                data.assignee_id,
                organization_id
            )
            if not assignee:
                raise ValueError("Assignee not found in your organization")
        
        task = Task(
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            organization_id=organization_id,
            assignee_id=data.assignee_id
        )
        
        task = await self.task_repo.create(task)
        
        # Trigger background notification
        send_task_created_notification.delay(
            task_id=task.id,
            organization_id=organization_id
        )
        
        return task
    
    async def get_task(
        self,
        task_id: int,
        organization_id: int
    ) -> Optional[Task]:
        """Get a task by ID."""
        return await self.task_repo.get_by_id(task_id, organization_id)
    
    async def list_tasks(
        self,
        organization_id: int,
        pagination: PaginationParams
    ) -> PaginatedResponse[TaskResponse]:
        """List tasks with pagination."""
        tasks = await self.task_repo.get_all(
            organization_id=organization_id,
            skip=pagination.offset,
            limit=pagination.limit
        )
        total = await self.task_repo.count(organization_id)
        
        # Convert SQLAlchemy models to Pydantic schemas
        task_responses = [TaskResponse.model_validate(task) for task in tasks]
        
        return PaginatedResponse(
            items=task_responses,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size
        )
    
    async def update_task(
        self,
        task_id: int,
        organization_id: int,
        data: TaskUpdate
    ) -> Optional[Task]:
        """Update a task."""
        # Verify assignee if being updated
        if data.assignee_id is not None:
            assignee = await self.user_repo.get_by_id(
                data.assignee_id,
                organization_id
            )
            if not assignee:
                raise ValueError("Assignee not found in your organization")
        
        update_data = data.dict(exclude_unset=True)
        return await self.task_repo.update(task_id, organization_id, update_data)
    
    async def delete_task(
        self,
        task_id: int,
        organization_id: int
    ) -> bool:
        """Delete a task."""
        return await self.task_repo.delete(task_id, organization_id)
