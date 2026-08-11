import json

import telemetry


def make_service(tmp_path, monkeypatch):
    service = telemetry.TelemetryService()
    # Redirect the service to an isolated telemetry file for each test.
    monkeypatch.setattr(service, "local_file", str(tmp_path / "telemetry.json"))
    return service


def write_telemetry(path, data):
    path.write_text(json.dumps(data))


def test_missing_file_returns_empty_list(tmp_path, monkeypatch):
    service = make_service(tmp_path, monkeypatch)
    assert service.get_active_threats() == []


def test_filters_out_closed_threats(tmp_path, monkeypatch):
    service = make_service(tmp_path, monkeypatch)
    data = [
        {"id": 1, "Status": "Open"},
        {"id": 2, "Status": "Closed"},
        {"id": 3, "Status": "Investigating"},
    ]
    write_telemetry(tmp_path / "telemetry.json", data)

    active = service.get_active_threats()
    ids = [t["id"] for t in active]
    assert ids == [1, 3]


def test_threats_without_status_are_considered_active(tmp_path, monkeypatch):
    service = make_service(tmp_path, monkeypatch)
    write_telemetry(tmp_path / "telemetry.json", [{"id": 1}])
    assert service.get_active_threats() == [{"id": 1}]


def test_malformed_json_returns_empty_list(tmp_path, monkeypatch):
    service = make_service(tmp_path, monkeypatch)
    (tmp_path / "telemetry.json").write_text("{ not valid json")
    assert service.get_active_threats() == []


def test_get_ingestion_metrics_shape(tmp_path, monkeypatch):
    service = make_service(tmp_path, monkeypatch)
    metrics = service.get_ingestion_metrics()
    assert metrics["status"] == "HEALTHY"
    assert metrics["health_pct"] == 98.4
    assert metrics["throughput_kbps"] == 142.5
    # last_sync is a formatted HH:MM:SS timestamp
    assert metrics["last_sync"].count(":") == 2


def test_default_local_file_is_next_to_module():
    service = telemetry.TelemetryService()
    assert service.local_file.endswith("telemetry.json")
    assert service.base_path in service.local_file


def test_get_telemetry_service_returns_instance():
    service = telemetry.get_telemetry_service()
    assert isinstance(service, telemetry.TelemetryService)
