"""The change password page."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_CHANGE_PASSWORD
from framework.locators.change_password_locators import ChangePasswordLocators
from framework.pages.change_password_page_assertions import ChangePasswordPageAssertions


class ChangePasswordPage:
    """Actions on the change password page."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = ChangePasswordLocators(page)
        self.assertions = ChangePasswordPageAssertions(page)

    def navigate(self) -> None:
        """Open the page and wait until the form is ready."""
        self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_CHANGE_PASSWORD))
        self.assertions.loaded()

    def change(self, current: str, new: str) -> None:
        """Replace the current password with a new one."""
        self.loc.current_password_input.fill(current)
        self.loc.new_password_input.fill(new)
        self.loc.repeat_password_input.fill(new)
        self.loc.change_button.click()
