"""Assertions on the login page."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from framework.locators.login_locators import LoginLocators
from framework.pages.login_constants import (
    INVALID_CREDENTIALS_MESSAGE,
    LOGIN_URL_PATTERN,
    SHOP_URL_PATTERN,
)


class LoginPageAssertions:
    """What the login page must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = LoginLocators(page)

    def loaded(self) -> None:
        """The login form is ready."""
        expect(self.loc.email_input).to_be_visible()

    def credentials_refused(self) -> None:
        """The form refuses the credentials and stays on the login page."""
        expect(self.loc.error_alert).to_have_text(INVALID_CREDENTIALS_MESSAGE)
        expect(self._page).to_have_url(re.compile(LOGIN_URL_PATTERN))

    def landed_on_shop(self) -> None:
        """A successful login lands on the product list."""
        expect(self._page).to_have_url(re.compile(SHOP_URL_PATTERN))
