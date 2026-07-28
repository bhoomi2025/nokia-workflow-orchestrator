from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobCreate(BaseModel):
    workbook_id: int
    inventory_id: int


class JobResponse(BaseModel):
    id: int
    workbook_id: int
    inventory_id: int
    submitted_by: int
    status: str
    result: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }