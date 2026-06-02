from fastapi import APIRouter

from app.services.monitoring_service import MonitoringService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/queues")
async def queues():
    return await MonitoringService.queue_status()


@router.get("/workers")
async def workers():
    return await MonitoringService.worker_status()


@router.get("/metrics")
async def metrics():
    return await MonitoringService.application_metrics()
