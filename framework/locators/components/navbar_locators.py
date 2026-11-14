"""Locators of the top bar, shown on every page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.navbar_constants import (
    ACCOUNT_MENU_NAME,
    BASKET_BUTTON_NAME,
    LOGIN_ITEM_NAME,
    LOGOUT_ITEM_NAME,
    OPEN_SEARCH_NAME,
    PROFILE_ITEM_NAME,
    SEARCH_TEST_ID,
)


class NavbarLocators:
    """The top bar: search, basket and account menu."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def open_search_button(self) -> Locator:
        """The magnifier that opens the search field."""
        return self._page.get_by_role("button", name=OPEN_SEARCH_NAME)

    @property
    def search_input(self) -> Locator:
        """The search field, inside the search bar's test id."""
        return self._page.get_by_test_id(SEARCH_TEST_ID).get_by_role("textbox")

    @property
    def basket_button(self) -> Locator:
        """The basket button, which also shows the item count."""
        return self._page.get_by_role("button", name=BASKET_BUTTON_NAME)

    @property
    def account_menu_button(self) -> Locator:
        """The button that opens the account menu."""
        return self._page.get_by_role("button", name=ACCOUNT_MENU_NAME)

    @property
    def profile_menu_item(self) -> Locator:
        """The account menu entry naming the signed-in user."""
        return self._page.get_by_role("menuitem", name=PROFILE_ITEM_NAME)

    @property
    def logout_menu_item(self) -> Locator:
        """The account menu entry that logs out."""
        return self._page.get_by_role("menuitem", name=LOGOUT_ITEM_NAME)

    @property
    def login_menu_item(self) -> Locator:
        """The account menu entry offered when nobody is signed in."""
        return self._page.get_by_role("menuitem", name=LOGIN_ITEM_NAME)
