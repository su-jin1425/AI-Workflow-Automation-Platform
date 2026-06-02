import asyncio

from celery import Celery

from app.core.config import settings
from app.execution.runner import run_workflow_execution

celery_app = Celery(
    "workflow_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={"app.tasks.execute_workflow_task": {"queue": "workflows"}},
)


@celery_app.task(name="app.tasks.execute_workflow_task")
def execute_workflow_task(execution_id: str) -> None:
    asyncio.run(run_workflow_execution(execution_id))
