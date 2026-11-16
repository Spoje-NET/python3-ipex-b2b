"""HTTP client for the IPEX B2B REST API (https://restapi.ipex.cz/documentation).

Authentication: ``POST /v1/token`` with ``{"username", "password"}`` returns an
``accessToken`` and ``expire``; the token is then sent *as is* (no ``Bearer``
prefix) in the ``Authorization`` header. The client logs in lazily, refreshes
shortly before expiry and retries once on HTTP 401.
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any

import requests

from .exceptions import IpexAuthError, IpexError
from .operations import OPERATIONS, Operation

DEFAULT_URL = "https://restapi.ipex.cz"
DEFAULT_TIMEOUT = 30.0
_REFRESH_MARGIN = 5.0  # seconds
_FALLBACK_TTL = 300.0  # used when the server's `expire` cannot be parsed


def _env_bool(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() not in ("0", "false", "no")


def _parse_expire(value: Any) -> float | None:
    """Best-effort conversion of IPEX ``expire`` to a unix timestamp."""
    if isinstance(value, (int, float)):
        return float(value) if value > 1e9 else time.time() + float(value)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S"):
                try:
                    return datetime.strptime(value, fmt).timestamp()
                except ValueError:
                    continue
    return None


class ApiClient:
    """Low-level client: authentication plus :meth:`call` for any endpoint."""

    def __init__(
        self,
        url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        *,
        verify: bool | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.url = (url or os.environ.get("IPEX_URL") or DEFAULT_URL).rstrip("/")
        self._username = username or os.environ.get("IPEX_LOGIN")
        self._password = password or os.environ.get("IPEX_PASSWORD")
        self.verify = (
            verify if verify is not None else _env_bool(os.environ.get("IPEX_VERIFY_SSL"), True)
        )
        self.timeout = timeout
        self.session = session or requests.Session()
        self._token: str | None = None
        self._expires_at = 0.0

    def __repr__(self) -> str:  # never leak credentials
        return f"<{type(self).__name__} url={self.url!r}>"

    # -- authentication -------------------------------------------------
    def login(self) -> str:
        if not self._username or not self._password:
            raise IpexAuthError("IPEX_LOGIN and IPEX_PASSWORD are required.")
        try:
            resp = self.session.post(
                f"{self.url}/v1/token",
                json={"username": self._username, "password": self._password},
                headers={"Accept": "application/json"},
                timeout=self.timeout,
                verify=self.verify,
            )
        except requests.RequestException as exc:
            raise IpexAuthError(f"Token request failed: {type(exc).__name__}") from None
        if resp.status_code != 200:
            raise IpexAuthError(f"Login refused by IPEX (HTTP {resp.status_code}).", resp.status_code)
        try:
            data = resp.json()
            token = data["accessToken"]
        except (ValueError, KeyError, TypeError):
            raise IpexAuthError("Unexpected token response from IPEX.") from None
        self._token = token
        self._expires_at = _parse_expire(data.get("expire")) or (time.time() + _FALLBACK_TTL)
        return token

    def token(self) -> str:
        if not self._token or time.time() >= self._expires_at - _REFRESH_MARGIN:
            self.login()
        assert self._token is not None
        return self._token

    # -- requests -------------------------------------------------------
    def call(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        body: Any = None,
        *,
        auth: bool = True,
    ) -> Any:
        """Perform one API request and return the decoded JSON (or text)."""
        query = {k: _fmt(v) for k, v in (params or {}).items() if v is not None}
        for attempt in (1, 2):
            headers = {"Accept": "application/json"}
            if auth:
                headers["Authorization"] = self.token()
            try:
                resp = self.session.request(
                    method.upper(),
                    f"{self.url}{path}",
                    params=query or None,
                    json=body if body is not None else None,
                    headers=headers,
                    timeout=self.timeout,
                    verify=self.verify,
                )
            except requests.RequestException as exc:
                raise IpexError(f"Request failed: {type(exc).__name__}") from None
            if resp.status_code == 401 and auth and attempt == 1:
                self._token = None
                continue
            break
        if resp.status_code >= 400:
            raise IpexError(f"IPEX API error HTTP {resp.status_code}: {_error_text(resp)}", resp.status_code)
        if not resp.content:
            return None
        try:
            return resp.json()
        except ValueError:
            return resp.text


def _fmt(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def _error_text(resp: requests.Response) -> str:
    try:
        data = resp.json()
    except ValueError:
        return resp.text[:300]
    if isinstance(data, dict):
        for key in ("message", "error", "detail"):
            if isinstance(data.get(key), str):
                return data[key][:300]
    return str(data)[:300]


def _make_method(op: Operation):
    def method(self: ApiClient, *args: Any, body: Any = None, **kwargs: Any) -> Any:
        names = op.path_params
        if len(args) > len(names):
            raise TypeError(f"{op.name}() takes {len(names)} positional argument(s)")
        path = op.path
        values = dict(zip(names, args))
        for n in names[len(args):]:
            if n not in kwargs:
                raise TypeError(f"{op.name}() missing path argument {n!r}")
            values[n] = kwargs.pop(n)
        for n, v in values.items():
            path = path.replace("{" + n + "}", requests.utils.quote(str(v), safe=""))
        unknown = set(kwargs) - set(op.query)
        if unknown:
            raise TypeError(f"{op.name}() unexpected argument(s): {sorted(unknown)}")
        missing = [q for q in op.required_query if kwargs.get(q) is None]
        if missing:
            raise TypeError(f"{op.name}() missing required argument(s): {missing}")
        if op.has_body and op.method != "DELETE" and body is None and op.method in ("POST", "PUT", "PATCH"):
            body = {}
        return self.call(op.method, path, kwargs, body)

    method.__name__ = op.name
    method.__doc__ = f"{op.summary}.\n\n``{op.method} {op.path}``"
    return method


class Ipex(ApiClient):
    """Full client: one method per IPEX REST operation (see :mod:`ipexb2b.operations`)."""


for _op in OPERATIONS:
    setattr(Ipex, _op.name, _make_method(_op))
