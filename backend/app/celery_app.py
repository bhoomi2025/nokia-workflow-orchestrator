from celery import Celery

# NOTE: For a real/public project this URL should come from an environment
# variable (e.g. os.environ["REDIS_URL"]), not be hardcoded. Kept inline here
# for simplicity during development — move it to a .env file before sharing
# this repo publicly, since it contains your Redis password.
REDIS_URL = "redis://default:LkProcM7mKSen7DiYEBAA9mMbD9KGxGA@small-wheel-tiger-52221.db.redis.io:18659"

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