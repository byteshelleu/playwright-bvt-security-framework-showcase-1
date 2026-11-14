"""Locators of the checkout screens: address, delivery, payment, review, confirmation."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.checkout_constants import (
    MASKED_CARD_TEMPLATE,
    PLACE_ORDER_NAME,
    REVIEW_TOTAL_ROW_NAME,
    THANK_YOU_HEADING,
    TO_DELIVERY_NAME,
    TO_PAYMENT_NAME,
    TO_REVIEW_NAME,
    TRACK_ORDERS_LINK,
)


class CheckoutLocators:
    """Every control the checkout walks through."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    def address_radio(self, street: str) -> Locator:
        """The radio of the saved address on this street.

        SCOPE: has_text narrows the rows to the one holding the street.
        """
        return self._page.get_by_role("row").filter(has_text=street).get_by_role("radio")

    @property
    def to_delivery_button(self) -> Locator:
        """Continue from the address step."""
        return self._page.get_by_role("button", name=TO_DELIVERY_NAME)

    def delivery_radio(self, method_name: str) -> Locator:
        """The radio of one delivery speed.

        SCOPE: has_text narrows the rows to the one naming the speed.
        """
        return self._page.get_by_role("row").filter(has_text=method_name).get_by_role("radio")

    @property
    def to_payment_button(self) -> Locator:
        """Continue from the delivery step."""
        return self._page.get_by_role("button", name=TO_PAYMENT_NAME)

    def card_radio(self, last_four: str) -> Locator:
        """The radio of the saved card ending in these digits.

        SCOPE: has_text narrows the rows to the one showing the masked number.
        """
        masked = MASKED_CARD_TEMPLATE.format(last_four=last_four)
        return self._page.get_by_role("row").filter(has_text=masked).get_by_role("radio")

    @property
    def to_review_button(self) -> Locator:
        """Continue from the payment step."""
        return self._page.get_by_role("button", name=TO_REVIEW_NAME)

    @property
    def place_order_button(self) -> Locator:
        """The button that places the order."""
        return self._page.get_by_role("button", name=PLACE_ORDER_NAME)

    @property
    def review_total_row(self) -> Locator:
        """The total line of the order summary."""
        return self._page.get_by_role("row", name=REVIEW_TOTAL_ROW_NAME)

    @property
    def thank_you_heading(self) -> Locator:
        """The confirmation heading."""
        return self._page.get_by_role("heading", name=THANK_YOU_HEADING)

    @property
    def track_orders_link(self) -> Locator:
        """The link to track the order just placed."""
        return self._page.get_by_role("link", name=TRACK_ORDERS_LINK)
