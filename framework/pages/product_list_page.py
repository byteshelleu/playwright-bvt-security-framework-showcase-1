"""The product list, the shop's landing page."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.components.navbar import Navbar
from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_SEARCH
from framework.helpers.records import Product
from framework.locators.product_list_locators import ProductListLocators
from framework.pages.product_list_page_assertions import ProductListPageAssertions


class ProductListPage:
    """Actions on the product list."""

    def __init__(self, page: Page) -> None:
        """Compose the locators, the assertions and the top bar."""
        self.page = page
        self.loc = ProductListLocators(page)
        self.assertions = ProductListPageAssertions(page)
        self.navbar = Navbar(page)

    def navigate(self) -> None:
        """Open the product list and wait until products are shown."""
        self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_SEARCH))
        self.assertions.loaded()

    def add_to_basket(self, product: Product) -> None:
        """Add one product to the basket from its card."""
        self.loc.add_to_basket_button(product.name).click()
