from celery import Celery
from redis.asyncio import Redis

from app.core.config import settings


class MonitoringService:
    @staticmethod
    async def queue_status() -> dict:
        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        try:
            queued = await redis.llen("celery")
            return {"queue": "celery", "queued_jobs": queued}
        finally:
            await redis.aclose()

    @staticmethod
    async def worker_status() -> dict:
        celery = Celery(broker=settings.redis_url, backend=settings.redis_url)
        inspection = celery.control.inspect(timeout=1)
        active = inspection.active() or {}
        registered = inspection.registered() or {}
        return {
            "workers": list(set(active.keys()) | set(registered.keys())),
            "active_tasks": active,
        }

    @staticmethod
    async def application_metrics() -> dict:
        queue = await MonitoringService.queue_status()
        workers = await MonitoringService.worker_status()
        return {"queue": queue, "workers": workers}
