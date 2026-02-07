from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER, nullable=False)
    
    # Multi-tenancy: user belongs to one organization
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    tasks = relationship("Task", back_populates="assignee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, org_id={self.organization_id})>"
