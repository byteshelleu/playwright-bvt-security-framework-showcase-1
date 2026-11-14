"""Assertions on the top bar."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.helpers.text_patterns import ends_with_number
from framework.locators.components.navbar_locators import NavbarLocators


class NavbarAssertions:
    """What the top bar must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = NavbarLocators(page)

    def signed_in_as(self, email: str) -> None:
        """The open account menu names this user."""
        expect(self.loc.profile_menu_item).to_contain_text(email)

    def signed_out(self) -> None:
        """The open account menu offers to log in."""
        expect(self.loc.login_menu_item).to_be_visible()

    def basket_count_is(self, count: int) -> None:
        """The basket button shows this many items."""
        expect(self.loc.basket_button).to_have_text(ends_with_number(count))
