from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.model.user import User
from app.utils.security import get_current_user
from app.schemas.flow_schemas import FlowCreate, FlowStepsUpdate, FlowRunRequest
from app.services.flow_services import (
    create_flow,
    get_all_flows,
    get_flow_by_id,
    update_flow_steps,
    run_flow,
)

router = APIRouter(prefix="/flows", tags=["Flows"])


@router.post("/")
def create(flow: FlowCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_flow(db, flow, owner_id=current_user.id)


@router.get("/")
def get_all(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_all_flows(db)


@router.get("/{flow_id}")
def get_by_id(flow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_flow_by_id(db, flow_id)


@router.put("/{flow_id}/steps")
def update_steps(flow_id: int, payload: FlowStepsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return update_flow_steps(db, flow_id, payload.steps)


@router.post("/{flow_id}/run")
def run(flow_id: int, payload: FlowRunRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return run_flow(db, flow_id, payload.inventory_id, submitted_by=current_user.id)