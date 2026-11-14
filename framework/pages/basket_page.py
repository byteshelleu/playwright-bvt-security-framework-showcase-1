"""The basket page."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_BASKET
from framework.helpers.records import Product
from framework.locators.basket_locators import BasketLocators
from framework.pages.basket_page_assertions import BasketPageAssertions


class BasketPage:
    """Actions on the basket page."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = BasketLocators(page)
        self.assertions = BasketPageAssertions(page)

    def navigate(self) -> None:
        """Open the basket and wait until it is ready."""
        self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_BASKET))
        self.assertions.loaded()

    def increase(self, product: Product) -> None:
        """Raise the product's quantity by one."""
        self.loc.increase_button(product.name).click()

    def decrease(self, product: Product) -> None:
        """Lower the product's quantity by one."""
        self.loc.decrease_button(product.name).click()

    def remove(self, product: Product) -> None:
        """Remove the product's line."""
        self.loc.remove_button(product.name).click()

    def checkout(self) -> None:
        """Start checkout."""
        self.loc.checkout_button.click()
