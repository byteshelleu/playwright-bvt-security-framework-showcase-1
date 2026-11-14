"""A thin client for security probes: it never raises on a status code,
so every test reads the status itself."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from playwright.sync_api import APIRequestContext, APIResponse

from framework.api_constants import LOGIN
from framework.helpers.records import ApiSession


class SecurityClient:
    """Raw requests, with or without a signed-in session."""

    def __init__(self, request: APIRequestContext) -> None:
        """Keep the request context bound to the shop."""
        self.request = request

    def get(
        self,
        path: str,
        session: ApiSession | None = None,
        params: Mapping[str, str] | None = None,
    ) -> APIResponse:
        """GET a path as the session, or anonymously."""
        headers = session.headers if session else None
        query: dict[str, str | float | bool] | None = dict(params) if params else None
        return self.request.get(path, params=query, headers=headers)

    def post(
        self, path: str, data: dict[str, Any], session: ApiSession | None = None
    ) -> APIResponse:
        """POST a body to a path as the session, or anonymously."""
        return self.request.post(path, data=data, headers=session.headers if session else None)

    def login(self, email: str, password: str) -> APIResponse:
        """Try a login with these credentials."""
        return self.request.post(LOGIN, data={"email": email, "password": password})
