"""The top bar shown on every page: search, basket, account menu."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.components.navbar_assertions import NavbarAssertions
from framework.locators.components.navbar_locators import NavbarLocators
from framework.pages.navbar_constants import SEARCH_SUBMIT_KEY


class Navbar:
    """Actions on the top bar."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.loc = NavbarLocators(page)
        self.assertions = NavbarAssertions(page)

    def search_for(self, term: str) -> None:
        """Search the catalogue for a term."""
        self.loc.open_search_button.click()
        self.loc.search_input.fill(term)
        self.loc.search_input.press(SEARCH_SUBMIT_KEY)

    def open_basket(self) -> None:
        """Open the basket from the top bar."""
        self.loc.basket_button.click()

    def open_account_menu(self) -> None:
        """Open the account menu."""
        self.loc.account_menu_button.click()

    def log_out(self) -> None:
        """Log out from the account menu."""
        self.open_account_menu()
        self.loc.logout_menu_item.click()
