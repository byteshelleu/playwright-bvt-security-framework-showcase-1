"""Security: endpoints that must check who is calling.

Each case first calls a route the customer may use, so a refusal next to it is
a real refusal and not a broken route.
"""

from __future__ import annotations

import pytest

from framework.api_constants import (
    ALL_ORDERS,
    AUTHENTICATION_DETAILS,
    CUSTOMER_DATA_ROUTES,
    ORDER_HISTORY,
    USERS,
    WHOAMI,
)
from framework.helpers.records import ApiSession
from framework.security.asserts import assert_live, assert_refused
from framework.security.client import SecurityClient
from framework.security.security_constants import NO_TOKEN_REFUSALS, ROLE_REFUSALS

pytestmark = pytest.mark.api


@pytest.mark.parametrize("route", CUSTOMER_DATA_ROUTES)
def test_authorization_token_required(
    security_client: SecurityClient, customer_session: ApiSession, route: str
) -> None:
    """Security: Routes holding customer data refuse a request without a token.

    Steps and expected results:
    1. Call the route with the customer's token -> it answers.
    2. Call it without a token -> it answers 401.
    """
    path = route.format(basket_id=customer_session.basket_id)
    assert_live(security_client.get(path, customer_session))

    assert_refused(security_client.get(path), NO_TOKEN_REFUSALS)


def test_authorization_all_orders(
    security_client: SecurityClient, customer_session: ApiSession
) -> None:
    """Security: A customer cannot list every customer's orders.

    Steps and expected results:
    1. Read the customer's own order history -> it is returned.
    2. Call the all-orders route as the customer -> it answers 403.
    """
    own_orders = security_client.get(ORDER_HISTORY, customer_session)
    assert_live(own_orders)

    all_orders = security_client.get(ALL_ORDERS, customer_session)
    assert_refused(all_orders, ROLE_REFUSALS)


def test_authorization_user_list(
    security_client: SecurityClient, customer_session: ApiSession
) -> None:
    """Security: A customer cannot list every user.

    Steps and expected results:
    1. Ask who the customer is -> it answers.
    2. Call the user list as the customer -> it answers 403.
    """
    identity = security_client.get(WHOAMI, customer_session)
    assert_live(identity)

    users = security_client.get(USERS, customer_session)
    assert_refused(users, ROLE_REFUSALS)


def test_authorization_auth_details(
    security_client: SecurityClient, customer_session: ApiSession
) -> None:
    """Security: A customer cannot read every user's authentication details.

    Steps and expected results:
    1. Ask who the customer is -> it answers.
    2. Call the authentication details as the customer -> it answers 403.
    """
    identity = security_client.get(WHOAMI, customer_session)
    assert_live(identity)

    response = security_client.get(AUTHENTICATION_DETAILS, customer_session)
    assert_refused(response, ROLE_REFUSALS)
