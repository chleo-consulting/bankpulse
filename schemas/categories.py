from uuid import UUID

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    parent_id: UUID | None
    icon: str | None

    model_config = {"from_attributes": True}


class CategoryWithChildrenResponse(BaseModel):
    id: UUID
    name: str
    icon: str | None
    children: list[CategoryResponse] = []

    model_config = {"from_attributes": True}
