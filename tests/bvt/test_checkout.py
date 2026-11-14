"""BVT: checkout."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from framework.helpers.seeder import Seeder
from framework.helpers.sign_in import sign_in_to_basket
from framework.pages.catalogue_constants import APPLE_JUICE, ONE_DAY_DELIVERY
from framework.pages.checkout_page import CheckoutPage

pytestmark = pytest.mark.bvt


def test_checkout_places_order(page: Page, seeder: Seeder, checkout_page: CheckoutPage) -> None:
    """BVT: A customer places an order with a saved address and card.

    Steps and expected results:
    1. Sign in with Apple Juice in the basket and start checkout -> the address step opens.
    2. Choose the saved address, One Day Delivery and the saved card -> the review
       totals the product and the delivery.
    3. Place the order -> the order is confirmed and can be tracked.
    """
    account = seeder.account("checkout")
    seeder.basket(account, APPLE_JUICE)
    address, card = seeder.address(account), seeder.card(account)
    basket = sign_in_to_basket(page, account)
    basket.checkout()

    checkout_page.choose_address(address)
    checkout_page.choose_delivery(ONE_DAY_DELIVERY)
    checkout_page.choose_card(card)
    checkout_page.assertions.review_total_is(APPLE_JUICE.price + ONE_DAY_DELIVERY.price)

    checkout_page.place_order()
    checkout_page.assertions.order_confirmed()
