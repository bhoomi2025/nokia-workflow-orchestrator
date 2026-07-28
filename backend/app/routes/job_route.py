from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.model.user import User
from app.utils.security import get_current_user
from app.schemas.job_schemas import JobCreate
from app.services.job_services import create_job, get_all_jobs, get_job_by_id

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/")
def submit(job: JobCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_job(db, job, submitted_by=current_user.id)


@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_jobs(db)


@router.get("/{job_id}")
def get_by_id(job_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_job_by_id(db, job_id)