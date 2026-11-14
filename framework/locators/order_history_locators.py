"""Locators of the order history page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.constants import XPATH_CARD_AROUND
from framework.pages.order_history_constants import (
    NO_ORDERS_IMAGE_NAME,
    ORDER_ID_TEMPLATE,
    TRACK_ORDER_NAME,
)


class OrderHistoryLocators:
    """The order cards and the empty state."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def order_cards(self) -> Locator:
        """Every order card, reached from its Track button.

        TIER 4: an order card has no role or test id; its Track button does,
        so the card is the nearest card around that button.
        """
        track = self._page.get_by_role("button", name=TRACK_ORDER_NAME)
        return track.locator(XPATH_CARD_AROUND)  # noqa: R008

    def order_card(self, order_id: str) -> Locator:
        """The card of one order.

        SCOPE: has_text narrows the cards to the one showing the order id.
        """
        return self.order_cards.filter(has_text=ORDER_ID_TEMPLATE.format(order_id=order_id))

    @property
    def no_orders_image(self) -> Locator:
        """The picture shown while there are no orders."""
        return self._page.get_by_role("img", name=NO_ORDERS_IMAGE_NAME)
