"""Assertions on the checkout screens."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.helpers.display import price_text
from framework.locators.checkout_locators import CheckoutLocators


class CheckoutPageAssertions:
    """What the checkout screens must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = CheckoutLocators(page)

    def review_total_is(self, amount: float) -> None:
        """The order summary totals the amount."""
        expect(self.loc.review_total_row).to_contain_text(price_text(amount))

    def order_confirmed(self) -> None:
        """The order is confirmed and can be tracked."""
        expect(self.loc.thank_you_heading).to_be_visible()
        expect(self.loc.track_orders_link).to_be_visible()
