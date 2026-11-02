from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel


class WorkbookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    content: Optional[str] = None


class WorkbookUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    change_notes: Optional[str] = None


class WorkbookImport(BaseModel):
    """Upload a hand-written workbook. `content` may be the JSON object itself or JSON text."""
    name: Optional[str] = None
    description: Optional[str] = None
    content: Union[dict, str]


class WorkbookValidateRequest(BaseModel):
    content: Union[dict, str]


class WorkbookResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    content: Optional[str]
    owner_id: int

    model_config = {
        "from_attributes": True
    }


class WorkbookVersionInfo(BaseModel):
    id: int
    workbook_id: int
    version_no: int
    change_notes: Optional[str]
    created_by: Optional[int]
    created_at: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


class WorkbookVersionDetail(WorkbookVersionInfo):
    content: Optional[str]
