"""Security: SQL injection on login and search."""

from __future__ import annotations

import pytest

from framework.api_constants import SEARCH
from framework.helpers.records import Account
from framework.security.asserts import assert_live, assert_no_server_error, assert_refused
from framework.security.client import SecurityClient
from framework.security.payloads import (
    PLAIN_SEARCH_TERM,
    SEARCH_PROBE_IDS,
    SEARCH_PROBES,
    SQL_TAUTOLOGY,
    UNKNOWN_EMAIL,
)
from framework.security.probes import search_query
from framework.security.security_constants import LOGIN_REFUSALS

pytestmark = pytest.mark.api


@pytest.mark.parametrize("probe", SEARCH_PROBES, ids=SEARCH_PROBE_IDS)
def test_injection_search(security_client: SecurityClient, probe: str) -> None:
    """Security: Search input never reaches SQL unescaped.

    Steps and expected results:
    1. Search for a plain term -> it answers, so the route is live.
    2. Search with the probe -> it answers without a server error.
    """
    plain = security_client.get(SEARCH, params=search_query(PLAIN_SEARCH_TERM))
    assert_live(plain)

    probed = security_client.get(SEARCH, params=search_query(probe))
    assert_no_server_error(probed)


def test_injection_login_password(
    security_client: SecurityClient, customer_account: Account
) -> None:
    """Security: SQL in the password field does not log anyone in.

    Steps and expected results:
    1. Log in with the customer's credentials -> it succeeds, so the route is live.
    2. Log in with a SQL tautology as the password -> it answers 401.
    """
    valid = security_client.login(customer_account.email, customer_account.password)
    assert_live(valid)

    probed = security_client.login(UNKNOWN_EMAIL, SQL_TAUTOLOGY)
    assert_refused(probed, LOGIN_REFUSALS)


def test_injection_login_email(security_client: SecurityClient, customer_account: Account) -> None:
    """Security: SQL in the email field does not log anyone in.

    Steps and expected results:
    1. Log in with the customer's credentials -> it succeeds, so the route is live.
    2. Log in with a SQL tautology as the email -> it answers 401.
    """
    valid = security_client.login(customer_account.email, customer_account.password)
    assert_live(valid)

    probed = security_client.login(SQL_TAUTOLOGY, UNKNOWN_EMAIL)
    assert_refused(probed, LOGIN_REFUSALS)
