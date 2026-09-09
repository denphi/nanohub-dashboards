"""
Unit tests for the session helper module (connect / env resolution).
"""
import os
import pytest
from unittest.mock import patch

from nanohubdashboard.session import (
    parse_env_file, resolve_credentials, create_session, DEFAULT_URL
)
from nanohubdashboard.exceptions import AuthenticationError


@pytest.fixture
def env_file(tmp_path):
    path = tmp_path / ".env"
    path.write_text(
        "# a comment\n"
        "export NANOHUB_TOKEN=\"secret-token\"\n"
        "NANOHUB_URL=https://dev.nanohub.org # inline comment\n"
        "QUOTED='single quoted'\n"
        "MALFORMED LINE\n"
        "EMPTY=\n"
    )
    return str(path)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ("NANOHUB_TOKEN", "NANOHUB_API_TOKEN", "NANOHUB_URL"):
        monkeypatch.delenv(var, raising=False)


class TestParseEnvFile:
    def test_parses_basic_values(self, env_file):
        values = parse_env_file(env_file)
        assert values["NANOHUB_TOKEN"] == "secret-token"
        assert values["NANOHUB_URL"] == "https://dev.nanohub.org"
        assert values["QUOTED"] == "single quoted"
        assert values["EMPTY"] == ""
        assert "MALFORMED LINE" not in values

    def test_missing_file_returns_empty(self):
        assert parse_env_file("/nonexistent/.env") == {}


class TestResolveCredentials:
    def test_explicit_args_win(self, env_file):
        creds = resolve_credentials(token="explicit", url="https://x.org/",
                                    env_file=env_file)
        assert creds["token"] == "explicit"
        assert creds["url"] == "https://x.org"

    def test_env_file_fallback(self, env_file):
        creds = resolve_credentials(env_file=env_file)
        assert creds["token"] == "secret-token"
        assert creds["url"] == "https://dev.nanohub.org"

    def test_environment_variable_beats_env_file(self, env_file, monkeypatch):
        monkeypatch.setenv("NANOHUB_TOKEN", "env-token")
        creds = resolve_credentials(env_file=env_file)
        assert creds["token"] == "env-token"

    def test_alternate_token_variable(self, monkeypatch):
        monkeypatch.setenv("NANOHUB_API_TOKEN", "alt-token")
        creds = resolve_credentials(env_file="/nonexistent/.env")
        assert creds["token"] == "alt-token"

    def test_defaults(self):
        creds = resolve_credentials(env_file="/nonexistent/.env")
        assert creds["token"] == ""
        assert creds["url"] == DEFAULT_URL


class TestCreateSession:
    def test_missing_token_raises(self):
        with pytest.raises(AuthenticationError):
            create_session(env_file="/nonexistent/.env")

    def test_session_created_with_personal_token(self, env_file):
        with patch("nanohubremote.Session") as MockSession:
            create_session(env_file=env_file)
            args, kwargs = MockSession.call_args
            assert args[0] == {"grant_type": "personal_token",
                               "token": "secret-token"}
            assert kwargs["url"] == "https://dev.nanohub.org/api"

    def test_url_api_suffix_not_duplicated(self):
        with patch("nanohubremote.Session") as MockSession:
            create_session(token="t", url="https://nanohub.org/api")
            args, kwargs = MockSession.call_args
            assert kwargs["url"] == "https://nanohub.org/api"
