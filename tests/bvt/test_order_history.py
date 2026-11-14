"""BVT: order history."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from framework.helpers.seeder import Seeder
from framework.helpers.sign_in import sign_in_to_order_history
from framework.pages.catalogue_constants import BANANA_JUICE, STANDARD_DELIVERY

pytestmark = pytest.mark.bvt


def test_order_history_lists_placed_order(page: Page, seeder: Seeder) -> None:
    """BVT: A placed order is listed with its total.

    Steps and expected results:
    1. With one Banana Juice order placed, sign in and open the order history ->
       the order is listed with its total.
    """
    account = seeder.account("orders")
    order = seeder.order(account, BANANA_JUICE, STANDARD_DELIVERY)

    orders = sign_in_to_order_history(page, account)
    orders.assertions.lists_order(order.order_id, order.total)


def test_order_history_empty_for_new_customer(page: Page, seeder: Seeder) -> None:
    """BVT: A customer who never ordered sees the empty state.

    Steps and expected results:
    1. Sign in as a new customer and open the order history -> it shows no orders.
    """
    account = seeder.account("no-orders")

    orders = sign_in_to_order_history(page, account)
    orders.assertions.shows_no_orders()
