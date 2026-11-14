"""Assertions on the registration page."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from framework.locators.registration_locators import RegistrationLocators
from framework.pages.login_constants import LOGIN_URL_PATTERN


class RegistrationPageAssertions:
    """What the registration page must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = RegistrationLocators(page)

    def loaded(self) -> None:
        """The sign-up form is ready."""
        expect(self.loc.email_input).to_be_visible()

    def registration_completed(self) -> None:
        """A completed sign-up hands over to the login page."""
        expect(self._page).to_have_url(re.compile(LOGIN_URL_PATTERN))
