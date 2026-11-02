from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from app.database.connection import get_db
from app.model.user import User
from app.utils.security import require_role
from app.schemas.workbook_schemas import (
    WorkbookCreate,
    WorkbookUpdate,
    WorkbookImport,
    WorkbookValidateRequest,
    WorkbookVersionInfo,
    WorkbookVersionDetail,
)
from app.services.workbook_services import (
    create_workbook,
    import_workbook,
    get_all_workbooks,
    get_workbook_by_id,
    update_workbook,
    delete_workbook,
    check_content,
    list_versions,
    get_version,
    restore_version,
    export_workbook_json,
)

router = APIRouter(prefix="/workbooks", tags=["Workbooks"])


@router.post("/")
def create(workbook: WorkbookCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("Editor"))):
    return create_workbook(db, workbook, owner_id=current_user.id)


@router.post("/import")
def import_json(payload: WorkbookImport, db: Session = Depends(get_db), current_user: User = Depends(require_role("Editor"))):
    return import_workbook(db, payload, owner_id=current_user.id)


@router.post("/validate")
def validate(payload: WorkbookValidateRequest, current_user: User = Depends(require_role("Viewer"))):
    """Check a draft without saving it."""
    return check_content(payload.content)


@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: User = Depends(require_role("Viewer"))):
    return get_all_workbooks(db)


@router.get("/{workbook_id}")
def get_by_id(workbook_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Viewer"))):
    return get_workbook_by_id(db, workbook_id)


@router.put("/{workbook_id}")
def update(workbook_id: int, workbook: WorkbookUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("Editor"))):
    return update_workbook(db, workbook_id, workbook, user_id=current_user.id)


@router.delete("/{workbook_id}")
def delete(workbook_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Editor"))):
    return delete_workbook(db, workbook_id)


@router.get("/{workbook_id}/export")
def export(workbook_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Viewer"))):
    filename, text = export_workbook_json(db, workbook_id)
    return Response(
        content=text,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{workbook_id}/versions", response_model=List[WorkbookVersionInfo])
def versions(workbook_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Viewer"))):
    return list_versions(db, workbook_id)


@router.get("/{workbook_id}/versions/{version_no}", response_model=WorkbookVersionDetail)
def version_detail(workbook_id: int, version_no: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Viewer"))):
    return get_version(db, workbook_id, version_no)


@router.post("/{workbook_id}/versions/{version_no}/restore")
def restore(workbook_id: int, version_no: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("Editor"))):
    return restore_version(db, workbook_id, version_no, user_id=current_user.id)
