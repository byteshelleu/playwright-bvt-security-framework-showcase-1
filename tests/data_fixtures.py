"""Fixtures for the API, cleanup and seeding."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from framework.config import Settings
from framework.helpers.api_client import ApiClient
from framework.helpers.cleanup import CleanupRegistrar
from framework.helpers.seeder import Seeder


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Where the shop runs; any host but this machine is refused."""
    return Settings()


@pytest.fixture(scope="session")
def api_request(playwright: Playwright, settings: Settings) -> Iterator[APIRequestContext]:
    """A request context bound to the shop."""
    request = playwright.request.new_context(base_url=settings.base_url)
    yield request
    request.dispose()


@pytest.fixture(scope="session")
def api_client(api_request: APIRequestContext) -> ApiClient:
    """The arrange channel the seeder and the account fixtures use."""
    return ApiClient(api_request)


@pytest.fixture(scope="session")
def session_cleanup(api_client: ApiClient) -> Iterator[CleanupRegistrar]:
    """Cleanup of the session-scoped accounts, swept when the worker ends."""
    registrar = CleanupRegistrar(api_client)
    yield registrar
    registrar.sweep()


@pytest.fixture
def cleanup_registrar(api_client: ApiClient) -> Iterator[CleanupRegistrar]:
    """Cleanup of what one test seeded, swept when the test ends."""
    registrar = CleanupRegistrar(api_client)
    yield registrar
    registrar.sweep()


@pytest.fixture
def seeder(api_client: ApiClient, cleanup_registrar: CleanupRegistrar) -> Seeder:
    """The one entry point a test seeds through."""
    return Seeder(api_client, cleanup_registrar)
