"""Assertions on the product list."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.helpers.display import price_text
from framework.helpers.records import Product
from framework.locators.product_list_locators import ProductListLocators


class ProductListPageAssertions:
    """What the product list must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = ProductListLocators(page)

    def loaded(self) -> None:
        """At least one product card is shown."""
        expect(self.loc.product_cards.first).to_be_visible()

    def results_for(self, term: str) -> None:
        """The results name the term searched for."""
        expect(self.loc.search_value_text).to_have_text(term)

    def shows_only(self, product: Product) -> None:
        """The product is the one card listed, with its price."""
        expect(self.loc.product_cards).to_have_count(1)
        expect(self.loc.product_card(product.name)).to_contain_text(price_text(product.price))

    def shows_no_products(self) -> None:
        """No product card is listed."""
        expect(self.loc.product_cards).to_have_count(0)
