"""Security: one customer reaching another customer's data (IDOR)."""

from __future__ import annotations

import pytest

from framework.api_constants import (
    ADDRESS_TEMPLATE,
    BASKET_ITEMS,
    BASKET_TEMPLATE,
    CARD_TEMPLATE,
    ORDER_HISTORY,
)
from framework.helpers.records import Account, ApiSession
from framework.helpers.seeder import Seeder
from framework.pages.catalogue_constants import APPLE_JUICE, STANDARD_DELIVERY
from framework.security.asserts import assert_live, assert_order_not_listed, assert_refused
from framework.security.client import SecurityClient
from framework.security.probes import basket_item
from framework.security.security_constants import (
    FOREIGN_BASKET_REFUSALS,
    FOREIGN_RECORD_REFUSALS,
)

pytestmark = pytest.mark.api


def test_idor_basket_write(
    security_client: SecurityClient,
    customer_session: ApiSession,
    other_customer_session: ApiSession,
) -> None:
    """Security: A customer cannot put items into another customer's basket.

    Steps and expected results:
    1. Add a product to the customer's own basket -> it is accepted.
    2. Add a product to the other customer's basket -> it is refused.
    """
    own = basket_item(APPLE_JUICE, customer_session.basket_id)
    assert_live(security_client.post(BASKET_ITEMS, own, customer_session))

    other = basket_item(APPLE_JUICE, other_customer_session.basket_id)
    response = security_client.post(BASKET_ITEMS, other, customer_session)
    assert_refused(response, FOREIGN_BASKET_REFUSALS)


def test_idor_basket_read(
    security_client: SecurityClient,
    customer_session: ApiSession,
    other_customer_session: ApiSession,
) -> None:
    """Security: A customer cannot read another customer's basket.

    Steps and expected results:
    1. Read the customer's own basket -> it is returned.
    2. Read the other customer's basket by id -> it is refused.
    """
    own = BASKET_TEMPLATE.format(basket_id=customer_session.basket_id)
    assert_live(security_client.get(own, customer_session))

    other = BASKET_TEMPLATE.format(basket_id=other_customer_session.basket_id)
    assert_refused(security_client.get(other, customer_session), FOREIGN_RECORD_REFUSALS)


def test_idor_address_read(
    security_client: SecurityClient,
    seeder: Seeder,
    customer_account: Account,
    customer_session: ApiSession,
    other_customer_account: Account,
) -> None:
    """Security: A customer cannot read another customer's saved address.

    Steps and expected results:
    1. Each customer saves an address; read the customer's own by id -> it is returned.
    2. Read the other customer's address by id -> it is refused.
    """
    own, other = seeder.address(customer_account), seeder.address(other_customer_account)
    own_route = ADDRESS_TEMPLATE.format(address_id=own.id)
    assert_live(security_client.get(own_route, customer_session))

    other_route = ADDRESS_TEMPLATE.format(address_id=other.id)
    assert_refused(security_client.get(other_route, customer_session), FOREIGN_RECORD_REFUSALS)


def test_idor_card_read(
    security_client: SecurityClient,
    seeder: Seeder,
    customer_account: Account,
    customer_session: ApiSession,
    other_customer_account: Account,
) -> None:
    """Security: A customer cannot read another customer's saved card.

    Steps and expected results:
    1. Each customer saves a card; read the customer's own by id -> it is returned.
    2. Read the other customer's card by id -> it is refused.
    """
    own, other = seeder.card(customer_account), seeder.card(other_customer_account)
    own_route = CARD_TEMPLATE.format(card_id=own.id)
    assert_live(security_client.get(own_route, customer_session))

    other_route = CARD_TEMPLATE.format(card_id=other.id)
    assert_refused(security_client.get(other_route, customer_session), FOREIGN_RECORD_REFUSALS)


def test_idor_order_history(
    security_client: SecurityClient,
    seeder: Seeder,
    customer_session: ApiSession,
    other_customer_account: Account,
) -> None:
    """Security: Order history lists only the customer's own orders.

    Steps and expected results:
    1. The other customer places an order -> it has an id.
    2. Read the customer's order history -> it is returned without that order.
    """
    order = seeder.order(other_customer_account, APPLE_JUICE, STANDARD_DELIVERY)

    history = security_client.get(ORDER_HISTORY, customer_session)
    assert_live(history)
    assert_order_not_listed(order.order_id, history)
