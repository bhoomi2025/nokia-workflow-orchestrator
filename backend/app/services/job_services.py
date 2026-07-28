from sqlalchemy.orm import Session

from app.model.job import Job
from app.model.workbook import Workbook
from app.model.inventory import Inventory
from app.schemas.job_schemas import JobCreate
from app.tasks.job_tasks import execute_job_task


def create_job(db: Session, job: JobCreate, submitted_by: int):

    workbook = db.query(Workbook).filter(Workbook.id == job.workbook_id).first()
    if not workbook:
        return {"message": "Workbook not found"}

    inventory = db.query(Inventory).filter(Inventory.id == job.inventory_id).first()
    if not inventory:
        return {"message": "Inventory not found"}

    new_job = Job(
        workbook_id=job.workbook_id,
        inventory_id=job.inventory_id,
        submitted_by=submitted_by,
        status="queued"
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Instead of running the job inline (which used to block this request for
    # ~2 seconds with time.sleep), we hand it off to the Celery worker and
    # return immediately. The frontend already polls /jobs/ to refresh status,
    # so it will pick up "running" and then "success"/"failed" on its own.
    execute_job_task.delay(new_job.id)

    return {
        "message": "Job submitted",
        "data": new_job
    }


def get_all_jobs(db: Session):
    return db.query(Job).order_by(Job.id.desc()).all()


def get_job_by_id(db: Session, job_id: int):
    return db.query(Job).filter(Job.id == job_id).first()