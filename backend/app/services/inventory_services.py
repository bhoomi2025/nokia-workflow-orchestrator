from sqlalchemy.orm import Session

from app.model.inventory import Inventory, Credential
from app.schemas.inventory_schemas import InventoryCreate, InventoryUpdate, CredentialCreate
from app.utils.encryption import encrypt_secret


def create_inventory(db: Session, inventory: InventoryCreate, owner_id: int):

    new_inventory = Inventory(
        name=inventory.name,
        description=inventory.description,
        hosts=inventory.hosts,
        groups=inventory.groups,
        owner_id=owner_id
    )

    db.add(new_inventory)
    db.commit()
    db.refresh(new_inventory)

    return {
        "message": "Inventory created successfully",
        "data": new_inventory
    }


def get_all_inventories(db: Session):
    return db.query(Inventory).all()


def get_inventory_by_id(db: Session, inventory_id: int):
    return (
        db.query(Inventory)
        .filter(Inventory.id == inventory_id)
        .first()
    )


def update_inventory(db: Session, inventory_id: int, inventory: InventoryUpdate):

    existing_inventory = (
        db.query(Inventory)
        .filter(Inventory.id == inventory_id)
        .first()
    )

    if not existing_inventory:
        return {"message": "Inventory not found"}

    if inventory.name is not None:
        existing_inventory.name = inventory.name

    if inventory.description is not None:
        existing_inventory.description = inventory.description

    if inventory.hosts is not None:
        existing_inventory.hosts = inventory.hosts

    if inventory.groups is not None:
        existing_inventory.groups = inventory.groups

    db.commit()
    db.refresh(existing_inventory)

    return {
        "message": "Inventory updated successfully",
        "data": existing_inventory
    }


def delete_inventory(db: Session, inventory_id: int):

    inventory = (
        db.query(Inventory)
        .filter(Inventory.id == inventory_id)
        .first()
    )

    if not inventory:
        return {"message": "Inventory not found"}

    db.delete(inventory)
    db.commit()

    return {
        "message": "Inventory deleted successfully"
    }


def set_credential(db: Session, inventory_id: int, credential: CredentialCreate):

    inventory = (
        db.query(Inventory)
        .filter(Inventory.id == inventory_id)
        .first()
    )

    if not inventory:
        return {"message": "Inventory not found"}

    encrypted = encrypt_secret(credential.password)

    new_credential = Credential(
        inventory_id=inventory_id,
        host_name=credential.host_name,
        username=credential.username,
        encrypted_secret=encrypted
    )

    db.add(new_credential)
    db.commit()
    db.refresh(new_credential)

    return {
        "message": "Credential saved successfully",
        "data": new_credential
    }


def get_credentials_for_inventory(db: Session, inventory_id: int):
    return (
        db.query(Credential)
        .filter(Credential.inventory_id == inventory_id)
        .all()
    )
