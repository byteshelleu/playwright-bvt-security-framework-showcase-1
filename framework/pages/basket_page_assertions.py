"""Assertions on the basket page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.helpers.display import price_text
from framework.helpers.records import Product
from framework.locators.basket_locators import BasketLocators
from framework.pages.basket_constants import LINE_TEMPLATE, TOTAL_TEMPLATE


class BasketPageAssertions:
    """What the basket must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = BasketLocators(page)

    def loaded(self) -> None:
        """The basket is ready."""
        expect(self.loc.checkout_button).to_be_visible()

    def contains(self, product: Product, quantity: int) -> None:
        """The product's line shows the quantity and the unit price."""
        line = LINE_TEMPLATE.format(quantity=quantity, price=price_text(product.price))
        expect(self.loc.basket_row(product.name)).to_contain_text(line)

    def total_is(self, amount: float) -> None:
        """The basket total equals the amount."""
        expect(self.loc.total_text).to_have_text(TOTAL_TEMPLATE.format(price=price_text(amount)))

    def is_empty(self) -> None:
        """No line is left and checkout is not offered."""
        expect(self.loc.basket_rows).to_have_count(0)
        expect(self.loc.checkout_button).to_be_disabled()
