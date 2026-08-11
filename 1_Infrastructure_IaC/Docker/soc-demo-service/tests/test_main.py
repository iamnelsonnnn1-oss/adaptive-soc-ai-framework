from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    return TestClient(main.app)


def test_utc_now_is_iso_utc():
    value = main.utc_now()
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() == timezone.utc.utcoffset(None)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "soc-demo-service"
    assert "timestamp" in body


def test_framework_endpoint(client):
    response = client.get("/framework")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "adaptive-soc-ai-framework"
    assert body["region"] == "eu-central-1"
    assert body["layers"] == ["terraform", "ansible", "docker"]
    assert set(body["handoff"]) == {"terraform", "ansible", "docker"}


def test_telemetry_endpoint(client):
    response = client.get("/telemetry")
    assert response.status_code == 200
    body = response.json()

    assert body["service"] == "soc-demo-service"
    assert body["summary"]["total_alerts"] == 3
    # Two alerts are not "triaged" (high + low) -> counted as open.
    assert body["summary"]["open_alerts"] == 2
    assert len(body["alerts"]) == 3

    alert_ids = {alert["id"] for alert in body["alerts"]}
    assert alert_ids == {"evt-1001", "evt-1002", "evt-1003"}


def test_openapi_metadata(client):
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Adaptive SOC Demo Service"
    assert schema["info"]["version"] == "1.0.0"
