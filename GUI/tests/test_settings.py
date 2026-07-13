import importlib

import streamlit as st

import settings


def reload_settings(monkeypatch, secrets=None, env=None):
    """Reload the settings module under controlled secrets/env conditions."""
    monkeypatch.setattr(st, "secrets", secrets or {}, raising=False)
    for key in ("GEMINI_MODEL", "GEMINI_API_KEY", "GOOGLE_API_KEY", "AWS_ACCESS_KEY_ID"):
        monkeypatch.delenv(key, raising=False)
    for key, value in (env or {}).items():
        monkeypatch.setenv(key, value)
    return importlib.reload(settings)


def test_default_model_falls_back_to_flash(monkeypatch):
    mod = reload_settings(monkeypatch)
    assert mod.DEFAULT_GEMINI_MODEL == "gemini-1.5-flash"


def test_default_model_prefers_secret(monkeypatch):
    mod = reload_settings(monkeypatch, secrets={"GEMINI_MODEL": "gemini-pro"})
    assert mod.DEFAULT_GEMINI_MODEL == "gemini-pro"


def test_default_model_uses_env_when_no_secret(monkeypatch):
    mod = reload_settings(monkeypatch, env={"GEMINI_MODEL": "gemini-env"})
    assert mod.DEFAULT_GEMINI_MODEL == "gemini-env"


def test_get_gemini_api_key_none_when_unset(monkeypatch):
    mod = reload_settings(monkeypatch)
    assert mod.get_gemini_api_key() is None


def test_get_gemini_api_key_prefers_secret(monkeypatch):
    mod = reload_settings(
        monkeypatch,
        secrets={"GEMINI_API_KEY": "secret-key"},
        env={"GEMINI_API_KEY": "env-key"},
    )
    assert mod.get_gemini_api_key() == "secret-key"


def test_get_gemini_api_key_falls_back_to_google_env(monkeypatch):
    mod = reload_settings(monkeypatch, env={"GOOGLE_API_KEY": "google-key"})
    assert mod.get_gemini_api_key() == "google-key"


def test_feature_flags_disabled_by_default(monkeypatch):
    mod = reload_settings(monkeypatch)
    assert mod.ENABLE_LIVE_AWS is False
    assert mod.ENABLE_AI_MENTOR is False


def test_feature_flags_enabled_with_credentials(monkeypatch):
    mod = reload_settings(
        monkeypatch,
        secrets={"AWS_ACCESS_KEY_ID": "AKIA"},
        env={"GEMINI_API_KEY": "key"},
    )
    assert mod.ENABLE_LIVE_AWS is True
    assert mod.ENABLE_AI_MENTOR is True


def test_urgency_map_covers_all_levels(monkeypatch):
    mod = reload_settings(monkeypatch)
    assert set(mod.URGENCY_MAP) == {"Low", "Medium", "High", "Critical"}
    assert mod.URGENCY_MAP["Critical"]["pulse"] is True
    assert mod.URGENCY_MAP["Low"]["pulse"] is False


def teardown_module(module):
    # Restore the module to a clean importable state for other test files.
    st.secrets = {}
    importlib.reload(settings)
