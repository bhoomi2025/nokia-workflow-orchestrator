from pydantic import BaseModel
from typing import Optional


class WorkbookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[str] = None


class WorkbookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None


class WorkbookResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    content: Optional[str]
    owner_id: int

    model_config = {
        "from_attributes": True
    }