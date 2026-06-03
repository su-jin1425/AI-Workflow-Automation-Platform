import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_queues_endpoint_exists():
    response = client.get(
        "/api/monitoring/queues"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )

def test_workers_endpoint_exists():
    response = client.get(
        "/api/monitoring/workers"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )

def test_metrics_endpoint_exists():
    response = client.get(
        "/api/monitoring/metrics"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )

def test_queues_returns_json():
    response = client.get(
        "/api/monitoring/queues"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )

def test_workers_returns_json():
    response = client.get(
        "/api/monitoring/workers"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )

def test_metrics_returns_json():
    response = client.get(
        "/api/monitoring/metrics"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )

def test_invalid_monitoring_route():
    response = client.get(
        "/api/monitoring/not-found"
    )

    assert response.status_code == 404

def test_metrics_response_content_type():
    response = client.get(
        "/api/monitoring/metrics"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )

def test_workers_response_content_type():
    response = client.get(
        "/api/monitoring/workers"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )

def test_queues_response_content_type():
    response = client.get(
        "/api/monitoring/queues"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )

@pytest.fixture(autouse=True)
def mock_monitoring_service():
    with patch("app.api.routes.monitoring.MonitoringService") as mock:
        mock.queue_status = AsyncMock(
            return_value={
                "queue": "celery",
                "queued_jobs": 5,
            }
        )
        mock.worker_status = AsyncMock(
            return_value={
                "workers": [
                    "worker-1",
                    "worker-2",
                ],
                "active_tasks": {
                    "worker-1": [],
                    "worker-2": [],
                },
            }
        )
        mock.application_metrics = AsyncMock(
            return_value={
                "queue": {
                    "queue": "celery",
                    "queued_jobs": 5,
                },
                "workers": {
                    "workers": [
                        "worker-1",
                        "worker-2",
                    ],
                    "active_tasks": {
                        "worker-1": [],
                        "worker-2": [],
                    },
                },
            }
        )
        yield mock

def test_queues_schema_validation(mock_monitoring_service):
    """Test that queues endpoint returns expected schema"""
    response = client.get("/api/monitoring/queues")

    if response.status_code == 200:
        data = response.json()
        assert "queue" in data
        assert "queued_jobs" in data

def test_workers_schema_validation(mock_monitoring_service):
    """Test that workers endpoint returns expected schema"""
    response = client.get("/api/monitoring/workers")

    if response.status_code == 200:
        data = response.json()
        assert "workers" in data
        assert "active_tasks" in data

def test_metrics_schema_validation(mock_monitoring_service):
    """Test that metrics endpoint returns expected schema"""
    response = client.get("/api/monitoring/metrics")

    if response.status_code == 200:
        data = response.json()
        assert "queue" in data
        assert "workers" in data
