from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.model.user import User
from app.utils.security import get_current_user
from app.schemas.inventory_schemas import (
    InventoryCreate,
    InventoryUpdate,
    CredentialCreate,
    CredentialResponse,
)
from app.services.inventory_services import (
    create_inventory,
    get_all_inventories,
    get_inventory_by_id,
    update_inventory,
    delete_inventory,
    set_credential,
    get_credentials_for_inventory,
)

router = APIRouter(prefix="/inventories", tags=["Inventories"])


@router.post("/")
def create(inventory: InventoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_inventory(db, inventory, owner_id=current_user.id)


@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_inventories(db)


@router.get("/{inventory_id}")
def get_by_id(inventory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_inventory_by_id(db, inventory_id)


@router.put("/{inventory_id}")
def update(inventory_id: int, inventory: InventoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_inventory(db, inventory_id, inventory)


@router.delete("/{inventory_id}")
def delete(inventory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_inventory(db, inventory_id)


@router.post("/{inventory_id}/hosts/{host_name}/credentials", response_model=CredentialResponse)
def add_credential(inventory_id: int, host_name: str, credential: CredentialCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    credential.host_name = host_name
    result = set_credential(db, inventory_id, credential)
    return result["data"]


@router.get("/{inventory_id}/credentials")
def list_credentials(inventory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_credentials_for_inventory(db, inventory_id)