from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class FlowCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FlowStepInput(BaseModel):
    position: int
    workbook_id: int
    var_overrides: Optional[Dict[str, Any]] = None
    on_error: Optional[str] = "stop"   

class FlowStepsUpdate(BaseModel):
    steps: List[FlowStepInput]


class FlowRunRequest(BaseModel):
    inventory_id: int