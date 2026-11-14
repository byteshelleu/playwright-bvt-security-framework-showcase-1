"""Security: brute-force protection on login."""

from __future__ import annotations

import pytest

from framework.helpers.seeder import Seeder
from framework.security.asserts import assert_live, assert_throttled
from framework.security.client import SecurityClient
from framework.security.payloads import LOGIN_BURST_ATTEMPTS
from framework.security.probes import failed_login_statuses

pytestmark = pytest.mark.api


def test_rate_limit_login(security_client: SecurityClient, seeder: Seeder) -> None:
    """Security: A burst of failed logins is throttled.

    The burst targets an account of its own, so no other case's account is locked.

    Steps and expected results:
    1. Log in with the right password -> it succeeds, so the route is live.
    2. Send 30 logins with wrong passwords -> the server starts answering 429.
    """
    account = seeder.account("rate-limit")
    assert_live(security_client.login(account.email, account.password))

    statuses = failed_login_statuses(security_client, account.email, LOGIN_BURST_ATTEMPTS)
    assert_throttled(statuses)
