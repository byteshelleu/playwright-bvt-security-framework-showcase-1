"""Locators of the basket page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.constants import XPATH_ICON_BUTTON
from framework.pages.basket_constants import (
    CHECKOUT_NAME,
    DECREASE_ICON,
    INCREASE_ICON,
    REMOVE_ICON,
    TOTAL_TEST_ID,
)


class BasketLocators:
    """The basket's lines, total and checkout button."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def basket_rows(self) -> Locator:
        """Every product line; the header row holds no cell."""
        return self._page.get_by_role("row").filter(has=self._page.get_by_role("cell"))

    def basket_row(self, product_name: str) -> Locator:
        """The line whose image names the product."""
        image = self._page.get_by_role("img", name=product_name, exact=True)
        return self.basket_rows.filter(has=image)

    def increase_button(self, product_name: str) -> Locator:
        """The unnamed + button of one line.

        TIER 4: the quantity buttons have no accessible name, so the icon they
        draw is the only handle.
        """
        return self.basket_row(product_name).locator(XPATH_ICON_BUTTON.format(icon=INCREASE_ICON))  # noqa: R008

    def decrease_button(self, product_name: str) -> Locator:
        """The unnamed - button of one line.

        TIER 4: the quantity buttons have no accessible name, so the icon they
        draw is the only handle.
        """
        return self.basket_row(product_name).locator(XPATH_ICON_BUTTON.format(icon=DECREASE_ICON))  # noqa: R008

    def remove_button(self, product_name: str) -> Locator:
        """The unnamed delete button of one line.

        TIER 4: the delete button has no accessible name, so the icon it draws
        is the only handle.
        """
        return self.basket_row(product_name).locator(XPATH_ICON_BUTTON.format(icon=REMOVE_ICON))  # noqa: R008

    @property
    def total_text(self) -> Locator:
        """The basket total."""
        return self._page.get_by_test_id(TOTAL_TEST_ID)

    @property
    def checkout_button(self) -> Locator:
        """The button that starts checkout."""
        return self._page.get_by_role("button", name=CHECKOUT_NAME)
