from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_overview_endpoint_exists():
    response = client.get(
        "/api/analytics/overview"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )


def test_executions_endpoint_exists():
    response = client.get(
        "/api/analytics/executions"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )


def test_system_health_endpoint_exists():
    response = client.get(
        "/api/analytics/system-health"
    )

    assert response.status_code in (
        200,
        401,
        403,
    )


def test_overview_returns_json():
    response = client.get(
        "/api/analytics/overview"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )


def test_executions_returns_json():
    response = client.get(
        "/api/analytics/executions"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )


def test_system_health_returns_json():
    response = client.get(
        "/api/analytics/system-health"
    )

    if response.status_code == 200:
        assert isinstance(
            response.json(),
            dict,
        )


def test_invalid_analytics_route():
    response = client.get(
        "/api/analytics/not-found"
    )

    assert response.status_code == 404


def test_overview_content_type():
    response = client.get(
        "/api/analytics/overview"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )


def test_executions_content_type():
    response = client.get(
        "/api/analytics/executions"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )


def test_system_health_content_type():
    response = client.get(
        "/api/analytics/system-health"
    )

    assert "application/json" in response.headers.get(
        "content-type",
        "",
    )