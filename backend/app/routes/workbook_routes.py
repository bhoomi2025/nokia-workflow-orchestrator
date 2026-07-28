from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.model.user import User
from app.utils.security import get_current_user
from app.schemas.workbook_schemas import WorkbookCreate, WorkbookUpdate
from app.services.workbook_services import (
    create_workbook,
    get_all_workbooks,
    get_workbook_by_id,
    update_workbook,
    delete_workbook,
)

router = APIRouter(prefix="/workbooks", tags=["Workbooks"])


@router.post("/")
def create(workbook: WorkbookCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_workbook(db, workbook, owner_id=current_user.id)


@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_workbooks(db)


@router.get("/{workbook_id}")
def get_by_id(workbook_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_workbook_by_id(db, workbook_id)


@router.put("/{workbook_id}")
def update(workbook_id: int, workbook: WorkbookUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_workbook(db, workbook_id, workbook)


@router.delete("/{workbook_id}")
def delete(workbook_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return delete_workbook(db, workbook_id)