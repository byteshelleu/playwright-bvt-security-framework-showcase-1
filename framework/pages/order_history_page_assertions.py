"""Assertions on the order history page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.helpers.display import price_text
from framework.locators.order_history_locators import OrderHistoryLocators


class OrderHistoryPageAssertions:
    """What the order history must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = OrderHistoryLocators(page)

    def lists_order(self, order_id: str, total: float) -> None:
        """The order has a card showing its total."""
        expect(self.loc.order_card(order_id)).to_contain_text(price_text(total))

    def shows_no_orders(self) -> None:
        """The empty state is shown and no order is listed."""
        expect(self.loc.no_orders_image).to_be_visible()
        expect(self.loc.order_cards).to_have_count(0)
