"""Assertions on the change password page."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.locators.change_password_locators import ChangePasswordLocators
from framework.pages.account_constants import PASSWORD_CHANGED_MESSAGE


class ChangePasswordPageAssertions:
    """What the change password page must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = ChangePasswordLocators(page)

    def loaded(self) -> None:
        """The form is ready."""
        expect(self.loc.current_password_input).to_be_visible()

    def password_changed(self) -> None:
        """The change is confirmed."""
        expect(self.loc.confirmation_status).to_have_text(PASSWORD_CHANGED_MESSAGE)
