"""Factories that generate the account fixtures, one per label.

conftest.py registers one `<label>_account` fixture per entry of
ACCOUNT_FIXTURE_LABELS. Each is session-scoped: the account is created once per
worker, its owned records are swept at the end, and its signed-in session is
saved on first sign-in and reused after that.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from framework.helpers.api_client import ApiClient
from framework.helpers.cleanup import CleanupRegistrar
from framework.helpers.records import Account
from framework.helpers.test_data import generate_account


def make_account_fixture(label: str) -> Callable[..., Account]:
    """A session fixture named `<label>_account` that creates the account once."""

    @pytest.fixture(scope="session", name=f"{label}_account")
    def account_fixture(api_client: ApiClient, session_cleanup: CleanupRegistrar) -> Account:
        """The generated account for this label, registered for cleanup first."""
        account = generate_account(label, reusable=True)
        session_cleanup.register(account)
        api_client.register(account)
        return account

    return account_fixture


def account_fixtures(labels: tuple[str, ...]) -> dict[str, Any]:
    """Every generated account fixture, keyed by its fixture name."""
    return {f"{label}_account": make_account_fixture(label) for label in labels}
