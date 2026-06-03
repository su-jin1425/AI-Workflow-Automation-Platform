import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app
from app.services.analytics_service import AnalyticsService

client = TestClient(app)

@pytest.fixture
def mock_analytics_service():
    with patch('app.api.routes.analytics.AnalyticsService') as mock:
        yield mock

def test_overview_endpoint(mock_analytics_service):
    """Test the analytics overview endpoint returns correct data structure"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_overview.return_value = {
        "workflows": 10,
        "executions": 50,
        "completed": 45,
        "failed": 5
    }
    mock_analytics_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    
    data = response.json()
    assert "workflows" in data
    assert "executions" in data
    assert "completed" in data
    assert "failed" in data

def test_execution_summary_endpoint(mock_analytics_service):
    """Test the execution summary endpoint returns correct data structure"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_execution_summary.return_value = {
        "summary": [
            {"date": "2023-01-01", "count": 10},
            {"date": "2023-01-02", "count": 15}
        ]
    }
    mock_analytics_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/analytics/executions/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "summary" in data

def test_system_health_endpoint(mock_analytics_service):
    """Test the system health endpoint returns correct data structure"""
    # Mock the service response
    mock_service_instance = MagicMock()
    mock_service_instance.get_system_health.return_value = {
        "status": "healthy",
        "uptime": 3600,
        "memory_usage": 45.5
    }
    mock_analytics_service.return_value = mock_service_instance
    
    response = client.get("/api/v1/analytics/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "uptime" in data
    assert "memory_usage" in data