"""Hooks, session fixtures and fixture registration for both suites."""

from __future__ import annotations

from typing import Any

import pytest
from playwright.sync_api import Playwright, expect

from framework.config import Settings
from framework.constants import ACCOUNT_FIXTURE_LABELS, EXPECT_TIMEOUT_MS, TEST_ID_ATTRIBUTE
from framework.helpers.session_cache import banner_cookies
from tests.data_fixtures import (  # noqa: F401
    api_client,
    api_request,
    cleanup_registrar,
    seeder,
    session_cleanup,
    settings,
)
from tests.fixtures_factory import account_fixtures
from tests.page_fixtures import (  # noqa: F401
    basket_page,
    checkout_page,
    login_page,
    navbar,
    product_list_page,
    registration_page,
)

pytest_plugins = ["framework.reporting.plugin", "pytester"]

globals().update(account_fixtures(ACCOUNT_FIXTURE_LABELS))


def pytest_configure(config: pytest.Config) -> None:
    """Every assertion in the suites waits the same time."""
    expect.set_options(timeout=EXPECT_TIMEOUT_MS)


@pytest.fixture(scope="session")
def base_url(settings: Settings) -> str:  # noqa: F811
    """The shop's address; only this machine is accepted."""
    return settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(
    browser_context_args: dict[str, Any], base_url: str, playwright: Playwright
) -> dict[str, Any]:
    """Strict selectors, the shop's address, its banners dismissed, and its test ids.

    Only browser tests request this fixture, so unit tests never start a browser.
    """
    playwright.selectors.set_test_id_attribute(TEST_ID_ATTRIBUTE)
    return {
        **browser_context_args,
        "base_url": base_url,
        "strict_selectors": True,
        "storage_state": {"cookies": banner_cookies(base_url), "origins": []},
    }
