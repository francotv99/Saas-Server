import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.workers.celery_app import celery_app
from app.config import settings
from app.models.task import Task
from app.repositories.task_repository import TaskRepository

logger = logging.getLogger(__name__)

# Create async engine for workers
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(name="send_task_created_notification")
def send_task_created_notification(task_id: int, organization_id: int):
    """
    Background task to send notification when a task is created.
    In production, this would send an email/webhook.
    For now, we log to console and Redis queue.
    """
    import asyncio
    
    async def _send_notification():
        async with AsyncSessionLocal() as session:
            task_repo = TaskRepository(session)
            task = await task_repo.get_by_id(task_id, organization_id)
            
            if task:
                # Mock email notification - log to console
                logger.info(
                    f"[NOTIFICATION] Task created: ID={task.id}, "
                    f"Title='{task.title}', Organization={organization_id}, "
                    f"Assignee={task.assignee_id or 'Unassigned'}"
                )
                
                # In production, you would:
                # 1. Send email via SES/SendGrid
                # 2. Send webhook to configured endpoints
                # 3. Update notification queue in Redis
                
                # Example mock implementation:
                notification_data = {
                    "type": "task_created",
                    "task_id": task.id,
                    "task_title": task.title,
                    "organization_id": organization_id,
                    "assignee_id": task.assignee_id,
                    "status": task.status.value,
                    "priority": task.priority.value
                }
                
                logger.info(f"[MOCK EMAIL] Would send to assignee: {notification_data}")
                return notification_data
            else:
                logger.warning(f"Task {task_id} not found for notification")
                return None
    
    return asyncio.run(_send_notification())
