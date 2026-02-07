from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False, index=True)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Multi-tenancy: task belongs to one organization
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Task assignment
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    organization = relationship("Organization", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, org_id={self.organization_id})>"
