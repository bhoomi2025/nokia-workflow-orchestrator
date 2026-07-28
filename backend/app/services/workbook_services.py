from sqlalchemy.orm import Session

from app.model.workbook import Workbook
from app.schemas.workbook_schemas import WorkbookCreate, WorkbookUpdate


def create_workbook(db: Session, workbook: WorkbookCreate, owner_id: int):

    new_workbook = Workbook(
        name=workbook.name,
        description=workbook.description,
        content=workbook.content,
        owner_id=owner_id
    )

    db.add(new_workbook)
    db.commit()
    db.refresh(new_workbook)

    return {
        "message": "Workbook created successfully",
        "data": new_workbook
    }


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
    workbook: WorkbookUpdate
):

    existing_workbook = (
        db.query(Workbook)
        .filter(Workbook.id == workbook_id)
        .first()
    )

    if not existing_workbook:
        return {"message": "Workbook not found"}

    if workbook.name is not None:
        existing_workbook.name = workbook.name

    if workbook.description is not None:
        existing_workbook.description = workbook.description

    if workbook.content is not None:
        existing_workbook.content = workbook.content

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

    db.delete(workbook)
    db.commit()

    return {
        "message": "Workbook deleted successfully"
    }