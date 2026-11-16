"""Exceptions raised by ipexb2b. Messages never contain credentials or tokens."""


class IpexError(Exception):
    """Base error for every failure talking to the IPEX REST API."""

    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class IpexAuthError(IpexError):
    """Missing/invalid credentials or the token endpoint refused the login."""
