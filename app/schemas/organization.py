from pydantic import BaseModel
from datetime import datetime


class OrganizationBase(BaseModel):
    name: str
    slug: str


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None


class OrganizationResponse(OrganizationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
