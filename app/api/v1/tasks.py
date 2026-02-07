from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import (
    get_current_user,
    get_current_organization_id,
    RequireMember
)
from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    PaginatedTasks
)
from app.services.task_service import TaskService
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = RequireMember,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    task_service = TaskService(db)
    try:
        task = await task_service.create_task(
            organization_id=organization_id,
            data=data,
            created_by_user_id=current_user.id
        )
        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=PaginatedTasks)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = RequireMember,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """List tasks with pagination."""
    task_service = TaskService(db)
    pagination = PaginationParams(page=page, page_size=page_size)
    result = await task_service.list_tasks(organization_id, pagination)
    
    return PaginatedTasks(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
        pages=result.pages
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = RequireMember,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """Get a task by ID."""
    task_service = TaskService(db)
    task = await task_service.get_task(task_id, organization_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = RequireMember,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    task_service = TaskService(db)
    try:
        task = await task_service.update_task(task_id, organization_id, data)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return TaskResponse.model_validate(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = RequireMember,
    organization_id: int = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    task_service = TaskService(db)
    deleted = await task_service.delete_task(task_id, organization_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
