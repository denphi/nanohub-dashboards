"""
Session helpers for connecting to the nanoHUB Dashboard API.

Provides a single ``connect()`` entry point that builds an authenticated
:class:`DashboardClient` from a personal token, taken from (in order of
precedence):

1. The ``token`` argument.
2. The ``NANOHUB_TOKEN`` (or ``NANOHUB_API_TOKEN``) environment variable.
3. A ``.env`` file (current directory by default, or ``env_file`` argument).

The nanoHUB instance URL is resolved the same way through the ``url``
argument or the ``NANOHUB_URL`` environment/.env variable, and defaults to
``https://nanohub.org``.
"""

import os
from pathlib import Path
from typing import Dict, Optional

from .exceptions import AuthenticationError

TOKEN_VARS = ("NANOHUB_TOKEN", "NANOHUB_API_TOKEN", "AUTH_TOKEN")
URL_VAR = "NANOHUB_URL"
DEFAULT_URL = "https://nanohub.org"


def parse_env_file(path) -> Dict[str, str]:
    """
    Parse a ``.env`` style file into a dictionary.

    Supports ``KEY=VALUE`` lines, ``export KEY=VALUE`` lines, comments
    (``#``) and single/double quoted values. Malformed lines are skipped.

    Args:
        path: Path to the .env file.

    Returns:
        Dictionary of variables found in the file (empty if unreadable).
    """
    values: Dict[str, str] = {}
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return values

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        # Strip surrounding quotes
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        else:
            # Drop trailing inline comments on unquoted values
            if " #" in value:
                value = value.split(" #", 1)[0].rstrip()
        values[key] = value
    return values


def resolve_credentials(token: Optional[str] = None,
                        url: Optional[str] = None,
                        env_file: Optional[str] = None) -> Dict[str, str]:
    """
    Resolve the token and base URL from arguments, environment, or .env file.

    Args:
        token: Personal access token (highest precedence).
        url: nanoHUB base URL, e.g. "https://nanohub.org" (highest precedence).
        env_file: Optional explicit path to a .env file. When omitted,
                  "./.env" is used if it exists.

    Returns:
        Dictionary with "token" and "url" keys. "token" may be empty
        if nothing was found.
    """
    env_values: Dict[str, str] = {}
    candidate = env_file or ".env"
    if env_file or Path(candidate).exists():
        env_values = parse_env_file(candidate)

    if not token:
        for var in TOKEN_VARS:
            token = os.environ.get(var) or env_values.get(var)
            if token:
                break

    if not url:
        url = os.environ.get(URL_VAR) or env_values.get(URL_VAR) or DEFAULT_URL

    return {"token": token or "", "url": url.rstrip("/")}


def create_session(token: Optional[str] = None,
                   url: Optional[str] = None,
                   env_file: Optional[str] = None,
                   **session_kwargs):
    """
    Create an authenticated nanohub-remote Session using a personal token.

    Args:
        token: Personal access token. Falls back to NANOHUB_TOKEN /
               NANOHUB_API_TOKEN in the environment or a .env file.
        url: nanoHUB base URL (with or without trailing "/api").
             Falls back to NANOHUB_URL, then https://nanohub.org.
        env_file: Optional explicit path to a .env file.
        **session_kwargs: Extra keyword arguments passed to Session
                          (timeout, max_retries, ...).

    Returns:
        nanohubremote.Session instance.

    Raises:
        AuthenticationError: If no token could be resolved.
        ImportError: If nanohub-remote is not installed.
    """
    try:
        from nanohubremote import Session
    except ImportError:
        raise ImportError(
            "nanohub-remote is required for API access. "
            "Install it with: pip install nanohub-remote"
        )

    creds = resolve_credentials(token=token, url=url, env_file=env_file)
    if not creds["token"]:
        raise AuthenticationError(
            "No nanoHUB token found. Pass token=..., set NANOHUB_TOKEN in the "
            "environment, or add NANOHUB_TOKEN=... to a .env file."
        )

    api_url = creds["url"]
    if not api_url.endswith("/api"):
        api_url = api_url + "/api"

    auth_data = {
        "grant_type": "personal_token",
        "token": creds["token"],
    }
    session_kwargs.setdefault("timeout", 30)
    return Session(auth_data, url=api_url, **session_kwargs)


def connect(token: Optional[str] = None,
            url: Optional[str] = None,
            env_file: Optional[str] = None,
            **session_kwargs):
    """
    Connect to the nanoHUB Dashboard API and return a DashboardClient.

    This is the recommended entry point for scripts:

        from nanohubdashboard import connect
        client = connect()                     # token from env or .env
        client = connect(token="...", url="https://dev.nanohub.org")

    Args:
        token: Personal access token (optional, see create_session).
        url: nanoHUB base URL (optional).
        env_file: Optional explicit path to a .env file.
        **session_kwargs: Extra keyword arguments for the Session.

    Returns:
        DashboardClient bound to an authenticated session.
    """
    from .client import DashboardClient

    creds = resolve_credentials(token=token, url=url, env_file=env_file)
    session = create_session(token=token, url=url, env_file=env_file,
                             **session_kwargs)
    return DashboardClient(session=session, base_url=creds["url"])
