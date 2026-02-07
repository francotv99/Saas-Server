from typing import TypeVar, Generic
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20
    
    def __init__(self, page: int = 1, page_size: int = 20, **kwargs):
        # Ensure page is at least 1
        page = max(1, page)
        # Limit page_size to reasonable range
        page_size = max(1, min(100, page_size))
        super().__init__(page=page, page_size=page_size, **kwargs)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
    
    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    
    @property
    def pages(self) -> int:
        if self.page_size == 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size
