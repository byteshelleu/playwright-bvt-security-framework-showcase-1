"""Locators of the change password page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.account_constants import (
    CHANGE_PASSWORD_NAME,
    CURRENT_PASSWORD_NAME,
    NEW_PASSWORD_NAME,
    REPEAT_PASSWORD_NAME,
)


class ChangePasswordLocators:
    """The change password form."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def current_password_input(self) -> Locator:
        """The current password field."""
        return self._page.get_by_role("textbox", name=CURRENT_PASSWORD_NAME)

    @property
    def new_password_input(self) -> Locator:
        """The new password field."""
        return self._page.get_by_role("textbox", name=NEW_PASSWORD_NAME)

    @property
    def repeat_password_input(self) -> Locator:
        """The field that repeats the new password."""
        return self._page.get_by_role("textbox", name=REPEAT_PASSWORD_NAME)

    @property
    def change_button(self) -> Locator:
        """The button that saves the new password."""
        return self._page.get_by_role("button", name=CHANGE_PASSWORD_NAME)

    @property
    def confirmation_status(self) -> Locator:
        """The status line confirming the change."""
        return self._page.get_by_role("status")
