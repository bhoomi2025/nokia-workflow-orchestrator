import json
from sqlalchemy.orm import Session

from app.model.flow import Flow, FlowStep
from app.model.workbook import Workbook
from app.schemas.flow_schemas import FlowCreate, FlowStepInput
from app.schemas.job_schemas import JobCreate
from app.services.job_services import create_job


def create_flow(db: Session, flow: FlowCreate, owner_id: int):

    new_flow = Flow(
        name=flow.name,
        description=flow.description,
        owner_id=owner_id
    )

    db.add(new_flow)
    db.commit()
    db.refresh(new_flow)

    return {
        "message": "Flow created successfully",
        "data": new_flow
    }


def get_all_flows(db: Session):
    return db.query(Flow).all()


def get_flow_by_id(db: Session, flow_id: int):

    flow = db.query(Flow).filter(Flow.id == flow_id).first()

    if not flow:
        return {"message": "Flow not found"}

    steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id)
        .order_by(FlowStep.position)
        .all()
    )

    return {
        "flow": flow,
        "steps": steps
    }


def update_flow_steps(db: Session, flow_id: int, steps: list[FlowStepInput]):

    flow = db.query(Flow).filter(Flow.id == flow_id).first()

    if not flow:
        return {"message": "Flow not found"}


    db.query(FlowStep).filter(FlowStep.flow_id == flow_id).delete()

    for step in steps:

        workbook = db.query(Workbook).filter(Workbook.id == step.workbook_id).first()
        if not workbook:
            db.rollback()
            return {"message": f"Workbook id {step.workbook_id} not found"}

        new_step = FlowStep(
            flow_id=flow_id,
            position=step.position,
            workbook_id=step.workbook_id,
            var_overrides=json.dumps(step.var_overrides) if step.var_overrides else None,
            on_error=step.on_error or "stop"
        )

        db.add(new_step)

    db.commit()

    return {"message": "Flow steps updated successfully"}


def run_flow(db: Session, flow_id: int, inventory_id: int, submitted_by: int):

    flow = db.query(Flow).filter(Flow.id == flow_id).first()

    if not flow:
        return {"message": "Flow not found"}

    steps = (
        db.query(FlowStep)
        .filter(FlowStep.flow_id == flow_id)
        .order_by(FlowStep.position)
        .all()
    )

    if not steps:
        return {"message": "Flow has no steps to run"}

    results = []

    for step in steps:

        job_result = create_job(
            db,
            JobCreate(workbook_id=step.workbook_id, inventory_id=inventory_id),
            submitted_by=submitted_by
        )

        job_status = job_result["data"].status if "data" in job_result else "failed"

        results.append({
            "workbook_id": step.workbook_id,
            "position": step.position,
            "status": job_status
        })


        if job_status == "failed" and step.on_error == "stop":
            return {
                "message": "Flow stopped due to failed step",
                "results": results
            }

    return {
        "message": "Flow completed",
        "results": results
    }