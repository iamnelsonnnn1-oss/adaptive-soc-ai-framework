from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import ai


@pytest.fixture
def offline_service(monkeypatch):
    """AICharlieService with no API key -> no client."""
    monkeypatch.setattr(ai, "get_gemini_api_key", lambda: None)
    return ai.AICharlieService()


@pytest.fixture
def online_service(monkeypatch):
    """AICharlieService with a mocked genai client."""
    monkeypatch.setattr(ai, "get_gemini_api_key", lambda: "test-key")
    fake_client = MagicMock()
    monkeypatch.setattr(ai.genai, "Client", MagicMock(return_value=fake_client))
    service = ai.AICharlieService()
    return service, fake_client


def test_no_key_yields_no_client(offline_service):
    assert offline_service.client is None
    assert offline_service.get_status() == "OFFLINE (DEGRADED)"


def test_client_init_failure_is_swallowed(monkeypatch):
    monkeypatch.setattr(ai, "get_gemini_api_key", lambda: "test-key")
    monkeypatch.setattr(ai.genai, "Client", MagicMock(side_effect=RuntimeError("boom")))
    service = ai.AICharlieService()
    assert service.client is None
    assert service.get_status() == "OFFLINE (DEGRADED)"


def test_online_status(online_service):
    service, _ = online_service
    assert service.client is not None
    assert service.get_status() == "ONLINE"


def test_check_connectivity_without_client(offline_service):
    ok, message = offline_service.check_connectivity()
    assert ok is False
    assert message == "Client not initialized."


def test_check_connectivity_success(online_service):
    service, client = online_service
    ok, message = service.check_connectivity()
    assert ok is True
    assert "Handshake Successful" in message
    client.models.generate_content.assert_called_once()


@pytest.mark.parametrize(
    "error, expected_fragment",
    [
        ("Error 401 API_KEY_INVALID", "Invalid credential baseline"),
        ("Error 429 quota exceeded", "API rate limit active"),
        ("Error 404 not found", "Model target unavailable"),
        ("restricted location error", "Restricted regional access"),
        ("some other failure", "Secure engine disconnect"),
    ],
)
def test_check_connectivity_error_mapping(online_service, error, expected_fragment):
    service, client = online_service
    client.models.generate_content.side_effect = Exception(error)
    ok, message = service.check_connectivity()
    assert ok is False
    assert expected_fragment in message


def test_analyze_incident_without_client(offline_service):
    result = offline_service.analyze_incident("what happened?", "ctx")
    assert result == "AI Mentorship unavailable. Manual protocol suggested."


def test_analyze_incident_success(online_service):
    service, client = online_service
    client.models.generate_content.return_value = SimpleNamespace(text="Contain the host.")
    result = service.analyze_incident("query", "context")
    assert result == "Contain the host."
    # Prompt should embed both the context and the question.
    _, kwargs = client.models.generate_content.call_args
    assert "context" in kwargs["contents"]
    assert "query" in kwargs["contents"]


def test_analyze_incident_silent_response(online_service):
    service, client = online_service
    client.models.generate_content.return_value = SimpleNamespace(text="")
    result = service.analyze_incident("query", "context")
    assert result == "Neural Link Error: Silent response from forensic engine."


@pytest.mark.parametrize(
    "error, expected_fragment",
    [
        ("Error 401 api_key_invalid", "Invalid credential baseline"),
        ("Error 429 quota", "API rate limit active"),
        ("Error 404 not found", "Model target unavailable"),
        ("location restricted", "Restricted regional access"),
        ("mystery failure", "Secure engine disconnect"),
    ],
)
def test_analyze_incident_error_mapping(online_service, error, expected_fragment):
    service, client = online_service
    client.models.generate_content.side_effect = Exception(error)
    result = service.analyze_incident("query", "context")
    assert result.startswith("Neural Link Error:")
    assert expected_fragment in result


def test_get_ai_service_returns_instance(monkeypatch):
    monkeypatch.setattr(ai, "get_gemini_api_key", lambda: None)
    service = ai.get_ai_service()
    assert isinstance(service, ai.AICharlieService)
