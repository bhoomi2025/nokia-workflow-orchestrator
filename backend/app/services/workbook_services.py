import json

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.model.workbook import Workbook, WorkbookVersion
from app.schemas.workbook_schemas import WorkbookCreate, WorkbookUpdate, WorkbookImport
from app.schemas.workbook_validation import validate_workbook

EMPTY_WORKBOOK = '{"workflows": []}'


def check_content(content):
    """Return {"valid", "errors", "warnings"} without saving anything."""
    errors, warnings = validate_workbook(content)
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def _require_valid(content):
    result = check_content(content)
    if not result["valid"]:
        raise HTTPException(
            status_code=422,
            detail={"message": "Workbook is not valid", "errors": result["errors"]},
        )


def _save_version(db: Session, workbook: Workbook, user_id, notes=None):
    last = (
        db.query(func.max(WorkbookVersion.version_no))
        .filter(WorkbookVersion.workbook_id == workbook.id)
        .scalar()
    ) or 0
    version = WorkbookVersion(
        workbook_id=workbook.id,
        version_no=last + 1,
        content=workbook.content,
        change_notes=notes,
        created_by=user_id,
    )
    db.add(version)
    return version


def create_workbook(db: Session, workbook: WorkbookCreate, owner_id: int, notes=None):

    content = workbook.content if workbook.content is not None else EMPTY_WORKBOOK
    _require_valid(content)

    new_workbook = Workbook(
        name=workbook.name,
        description=workbook.description,
        content=content,
        owner_id=owner_id
    )

    db.add(new_workbook)
    db.flush()  # gives new_workbook.id before the version row needs it
    _save_version(db, new_workbook, owner_id, notes or "Created")
    db.commit()
    db.refresh(new_workbook)

    return {
        "message": "Workbook created successfully",
        "data": new_workbook
    }


def import_workbook(db: Session, payload: WorkbookImport, owner_id: int):
    content = payload.content
    if isinstance(content, str):
        _require_valid(content)  # reports bad JSON clearly
        parsed = json.loads(content)
    else:
        parsed = content
        content = json.dumps(parsed, indent=2)
    _require_valid(content)

    name = payload.name or (parsed.get("name") if isinstance(parsed.get("name"), str) else None) or "Imported workbook"
    description = payload.description or (parsed.get("description") if isinstance(parsed.get("description"), str) else None)
    return create_workbook(
        db,
        WorkbookCreate(name=name, description=description, content=content),
        owner_id,
        notes="Imported from JSON",
    )


def get_all_workbooks(db: Session):
    return db.query(Workbook).all()


def get_workbook_by_id(db: Session, workbook_id: int):
    return (
        db.query(Workbook)
        .filter(Workbook.id == workbook_id)
        .first()
    )


def update_workbook(
    db: Session,
    workbook_id: int,
    workbook: WorkbookUpdate,
    user_id=None
):

    existing_workbook = (
        db.query(Workbook)
        .filter(Workbook.id == workbook_id)
        .first()
    )

    if not existing_workbook:
        return {"message": "Workbook not found"}

    content_changed = (
        workbook.content is not None and workbook.content != existing_workbook.content
    )
    if content_changed:
        _require_valid(workbook.content)

    if workbook.name is not None:
        existing_workbook.name = workbook.name

    if workbook.description is not None:
        existing_workbook.description = workbook.description

    if content_changed:
        existing_workbook.content = workbook.content
        _save_version(db, existing_workbook, user_id, workbook.change_notes)

    db.commit()
    db.refresh(existing_workbook)

    return {
        "message": "Workbook updated successfully",
        "data": existing_workbook
    }


def delete_workbook(db: Session, workbook_id: int):

    workbook = (
        db.query(Workbook)
        .filter(Workbook.id == workbook_id)
        .first()
    )

    if not workbook:
        return {"message": "Workbook not found"}

    db.query(WorkbookVersion).filter(WorkbookVersion.workbook_id == workbook_id).delete()
    db.delete(workbook)
    db.commit()

    return {
        "message": "Workbook deleted successfully"
    }


def list_versions(db: Session, workbook_id: int):
    if not get_workbook_by_id(db, workbook_id):
        raise HTTPException(status_code=404, detail="Workbook not found")
    return (
        db.query(WorkbookVersion)
        .filter(WorkbookVersion.workbook_id == workbook_id)
        .order_by(WorkbookVersion.version_no.desc())
        .all()
    )


def get_version(db: Session, workbook_id: int, version_no: int):
    version = (
        db.query(WorkbookVersion)
        .filter(
            WorkbookVersion.workbook_id == workbook_id,
            WorkbookVersion.version_no == version_no,
        )
        .first()
    )
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


def restore_version(db: Session, workbook_id: int, version_no: int, user_id: int):
    version = get_version(db, workbook_id, version_no)
    workbook = get_workbook_by_id(db, workbook_id)
    workbook.content = version.content
    _save_version(db, workbook, user_id, f"Restored from version {version_no}")
    db.commit()
    db.refresh(workbook)
    return {"message": f"Restored version {version_no} as a new version", "data": workbook}


def export_workbook_json(db: Session, workbook_id: int):
    """Returns (filename, pretty JSON text) - the same file the CLI would accept."""
    workbook = get_workbook_by_id(db, workbook_id)
    if not workbook:
        raise HTTPException(status_code=404, detail="Workbook not found")
    try:
        text = json.dumps(json.loads(workbook.content or EMPTY_WORKBOOK), indent=2)
    except json.JSONDecodeError:
        text = workbook.content or EMPTY_WORKBOOK
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in workbook.name) or "workbook"
    return f"{safe}.json", text
