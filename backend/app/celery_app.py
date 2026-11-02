import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Redis URL .env file se aata hai, code mein password nahi likhna
REDIS_URL = os.environ["REDIS_URL"]

celery_app = Celery(
    "workflow_orchestrator",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Tells Celery where to find task functions when the worker starts.
celery_app.autodiscover_tasks(["app.tasks"])
from app.tasks import job_tasks