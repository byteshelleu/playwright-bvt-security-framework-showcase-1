"""BVT: the basket.

The cases share the shopper account, so they are one xdist group and never run at
once. Each starts from an empty basket and seeds what it needs; the seeder sweeps
the basket after every case.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from framework.ci_constants import XDIST_GROUP_BASKET
from framework.helpers.records import Account
from framework.helpers.seeder import Seeder
from framework.helpers.sign_in import sign_in_to_basket, sign_in_to_shop
from framework.pages.basket_constants import RAISED_QUANTITY
from framework.pages.basket_page import BasketPage
from framework.pages.catalogue_constants import APPLE_JUICE

pytestmark = [pytest.mark.bvt, pytest.mark.xdist_group(XDIST_GROUP_BASKET)]


@pytest.fixture
def shopper(seeder: Seeder, shopper_account: Account) -> Account:
    """The shared shopper, its basket swept when the case ends."""
    return seeder.reuse(shopper_account)


def test_basket_add_product(page: Page, shopper: Account, basket_page: BasketPage) -> None:
    """BVT: A product added from the list reaches the basket.

    Steps and expected results:
    1. Sign in and add Apple Juice from the product list -> the basket counter shows 1.
    2. Open the basket -> Apple Juice is listed once.
    """
    shop = sign_in_to_shop(page, shopper)
    shop.add_to_basket(APPLE_JUICE)
    shop.navbar.assertions.basket_count_is(1)

    shop.navbar.open_basket()
    basket_page.assertions.contains(APPLE_JUICE, quantity=1)


def test_basket_quantity_updates_total(page: Page, shopper: Account, seeder: Seeder) -> None:
    """BVT: Raising a quantity updates the line and the total.

    Steps and expected results:
    1. With Apple Juice in the basket, sign in and open the basket -> it is listed.
    2. Raise its quantity -> the line shows 2 and the total doubles.
    """
    seeder.basket(shopper, APPLE_JUICE)
    basket = sign_in_to_basket(page, shopper)

    basket.increase(APPLE_JUICE)
    basket.assertions.contains(APPLE_JUICE, quantity=RAISED_QUANTITY)
    basket.assertions.total_is(APPLE_JUICE.price * RAISED_QUANTITY)


def test_basket_remove_leaves_empty(page: Page, shopper: Account, seeder: Seeder) -> None:
    """BVT: Removing the only product empties the basket.

    Steps and expected results:
    1. With Apple Juice in the basket, sign in and open the basket -> it is listed.
    2. Remove it -> no line is left and checkout is not offered.
    """
    seeder.basket(shopper, APPLE_JUICE)
    basket = sign_in_to_basket(page, shopper)

    basket.remove(APPLE_JUICE)
    basket.assertions.is_empty()
