from pydantic import BaseModel
from typing import Optional


class InventoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    hosts: Optional[str] = None
    groups: Optional[str] = None


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    hosts: Optional[str] = None
    groups: Optional[str] = None


class InventoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    hosts: Optional[str]
    groups: Optional[str]
    owner_id: int

    model_config = {
        "from_attributes": True
    }


class CredentialCreate(BaseModel):
    host_name: str
    username: str
    password: str

class CredentialResponse(BaseModel):
    id: int
    inventory_id: int
    host_name: str
    username: str
    
    model_config = {
        "from_attributes": True
    }