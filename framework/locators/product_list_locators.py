"""Locators of the product list, which also shows search results."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.product_list_constants import ADD_TO_BASKET_NAME, SEARCH_VALUE_TEST_ID


class ProductListLocators:
    """The product cards and the search term above them."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def product_cards(self) -> Locator:
        """Every product card on the page."""
        return self._page.get_by_role("main").get_by_role("article")

    def product_card(self, product_name: str) -> Locator:
        """The card whose image names the product."""
        image = self._page.get_by_role("img", name=product_name, exact=True)
        return self.product_cards.filter(has=image)

    def add_to_basket_button(self, product_name: str) -> Locator:
        """The Add to Basket button on one product's card."""
        return self.product_card(product_name).get_by_role("button", name=ADD_TO_BASKET_NAME)

    @property
    def search_value_text(self) -> Locator:
        """The term the results were searched for."""
        return self._page.get_by_test_id(SEARCH_VALUE_TEST_ID)
