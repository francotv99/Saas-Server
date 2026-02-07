from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: UserRole


class UserCreate(UserBase):
    password: str
    organization_id: int


class UserUpdate(BaseModel):
    full_name: str | None = None
    role: UserRole | None = None


class UserResponse(UserBase):
    id: int
    organization_id: int
    
    class Config:
        from_attributes = True
