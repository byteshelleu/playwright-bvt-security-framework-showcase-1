"""The order history page."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_ORDER_HISTORY
from framework.locators.order_history_locators import OrderHistoryLocators
from framework.pages.order_history_page_assertions import OrderHistoryPageAssertions


class OrderHistoryPage:
    """Actions on the order history page."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = OrderHistoryLocators(page)
        self.assertions = OrderHistoryPageAssertions(page)

    def navigate(self) -> None:
        """Open the order history; the caller checks what it lists."""
        self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_ORDER_HISTORY))
