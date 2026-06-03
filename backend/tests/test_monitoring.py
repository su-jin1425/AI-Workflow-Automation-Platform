import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.services.monitoring_service import MonitoringService

client = TestClient(app)

@pytest.fixture
def mock_monitoring_service():
    with patch('app.api.routes.monitoring.MonitoringService') as mock:
        yield mock

def test_queue_status(mock_monitoring_service):
    """Test the queue status endpoint returns correct data structure"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_queue_status.return_value = {
        "queue": {
            "pending": 5,
            "processing": 3,
            "failed": 1
        }
    }
    mock_monitoring_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/monitoring/queue")
    assert response.status_code == 200
    
    data = response.json()
    assert "queue" in data

def test_worker_status(mock_monitoring_service):
    """Test the worker status endpoint returns correct data structure"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_worker_status.return_value = {
        "workers": [
            {"id": "worker-1", "status": "active", "current_task": "task-123"},
            {"id": "worker-2", "status": "idle", "current_task": None}
        ]
    }
    mock_monitoring_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/monitoring/workers")
    assert response.status_code == 200
    
    data = response.json()
    assert "workers" in data

def test_metrics_status(mock_monitoring_service):
    """Test the metrics endpoint returns correct data structure"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_metrics.return_value = {
        "active_tasks": 3,
        "completed_tasks": 100,
        "failed_tasks": 5,
        "average_processing_time": 1.5
    }
    mock_monitoring_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/monitoring/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "active_tasks" in data