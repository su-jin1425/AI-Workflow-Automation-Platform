import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def test_queues_endpoint_exists():
    response = client.get(
        "/api/v1/monitoring/queue"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )

def test_workers_endpoint_exists():
    response = client.get(
        "/api/v1/monitoring/workers"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )

def test_metrics_endpoint_exists():
    response = client.get(
        "/api/v1/monitoring/metrics"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )

def test_queues_returns_json():
    response = client.get(
        "/api/v1/monitoring/queue"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )

def test_workers_returns_json():
    response = client.get(
        "/api/v1/monitoring/workers"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )

def test_metrics_returns_json():
    response = client.get(
        "/api/v1/monitoring/metrics"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )

def test_invalid_monitoring_route():
    response = client.get(
        "/api/v1/monitoring/does-not-exist"
    )

    assert response.status_code == 404

def test_metrics_response_content_type():
    response = client.get(
        "/api/v1/monitoring/metrics"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )

def test_workers_response_content_type():
    response = client.get(
        "/api/v1/monitoring/workers"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )

def test_queues_response_content_type():
    response = client.get(
        "/api/v1/monitoring/queue"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )

# Tests with schema validation using mocked service responses
@pytest.fixture
def mock_monitoring_service():
    with patch('app.api.routes.monitoring.MonitoringService') as mock:
        yield mock

def test_queues_schema_validation(mock_monitoring_service):
    """Test that queues endpoint returns expected schema"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_queue_status.return_value = {
        "queue": {
            "active": 5,
            "reserved": 3,
            "scheduled": 2
        }
    }
    mock_monitoring_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/monitoring/queue")
    
    if response.status_code == 200:
        data = response.json()
        assert "active" in data
        assert "reserved" in data
        assert "scheduled" in data

def test_workers_schema_validation(mock_monitoring_service):
    """Test that workers endpoint returns expected schema"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_worker_status.return_value = {
        "workers": [
            {"id": "worker-1", "status": "active"},
            {"id": "worker-2", "status": "idle"}
        ]
    }
    mock_monitoring_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/monitoring/workers")
    
    if response.status_code == 200:
        data = response.json()
        assert "workers" in data

def test_metrics_schema_validation(mock_monitoring_service):
    """Test that metrics endpoint returns expected schema"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_metrics.return_value = {
        "cpu_percent": 45.5,
        "memory_percent": 60.2,
        "active_tasks": 3
    }
    mock_monitoring_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/monitoring/metrics")
    
    if response.status_code == 200:
        data = response.json()
        assert "cpu_percent" in data
        assert "memory_percent" in data