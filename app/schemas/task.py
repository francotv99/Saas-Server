from pydantic import BaseModel
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee_id: int | None = None


class TaskResponse(TaskBase):
    id: int
    organization_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaginatedTasks(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
    pages: int
