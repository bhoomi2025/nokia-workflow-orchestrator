import json
from datetime import datetime, timezone

from app.celery_app import celery_app
from app.database.connection import SessionLocal
from app.model.job import Job
from app.model.workbook import Workbook
from app.model.inventory import Inventory, Credential
from app.utils.encryption import decrypt_secret
from app.engine.orchestrator import run_workbook
from app.engine.models import RunOptions


def _build_inventory_dict(inventory: Inventory, db) -> dict:
    """Inventory ke saved JSON (hosts/groups) ko lo, aur uske saath
    DB mein alag se stored credentials (username/password) ko jod do.
    Password abhi tak encrypted state mein DB mein pada tha -- yahan
    use decrypt karke asli password nikala jata hai."""
    hosts = json.loads(inventory.hosts) if inventory.hosts else {}
    groups = json.loads(inventory.groups) if inventory.groups else {}

    credentials = db.query(Credential).filter(
        Credential.inventory_id == inventory.id
    ).all()

    for cred in credentials:
        host = hosts.setdefault(cred.host_name, {})
        host.setdefault("user_matrix", [])
        host["user_matrix"].append({
            "username": cred.username,
            "password": decrypt_secret(cred.encrypted_secret),
        })

    return {"hosts": hosts, "groups": groups}


@celery_app.task(name="execute_job_task")
def execute_job_task(job_id: int):
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"message": f"Job {job_id} not found"}

        workbook = db.query(Workbook).filter(Workbook.id == job.workbook_id).first()
        inventory = db.query(Inventory).filter(Inventory.id == job.inventory_id).first()

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

        # Workbook ka content DB mein JSON text ke roop mein saved hai --
        # usko wapas Python dict mein convert karna padega.
        workbook_dict = json.loads(workbook.content) if workbook.content else {"workflows": []}
        inventory_dict = _build_inventory_dict(inventory, db)

        collected_output = []

        options = RunOptions(
            workdir=f"/tmp/job_{job_id}",
            extra_vars={},
            tags=None,
            skip_tags=None,
            workflows=None,
            only_tasks=None,
            should_cancel=None,
            on_output=lambda line: collected_output.append(line),
            timeout=300,
        )

        result = run_workbook(workbook_dict, inventory_dict, options)

        job.status = result.status
        job.finished_at = result.finished_at

        # Har task ka result ek chhoti summary ke roop mein save kar do,
        # taaki frontend pe dikhaya ja sake ki kaunsa step pass/fail hua.
        task_summary = [
            {
                "workflow": t.workflow,
                "task": t.task,
                "status": t.status,
                "exit_code": t.exit_code,
            }
            for t in result.task_results
        ]

        job.result = json.dumps({
            "status": result.status,
            "tasks": task_summary,
            "output": collected_output,
            "error": result.error,
        })

        db.commit()

        return {"message": "Job completed", "job_id": job_id, "status": job.status}
    finally:
        db.close()