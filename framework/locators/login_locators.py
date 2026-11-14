"""Locators of the login page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.login_constants import (
    LOGIN_BUTTON_NAME,
    LOGIN_EMAIL_NAME,
    LOGIN_PASSWORD_NAME,
)


class LoginLocators:
    """The login form."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def email_input(self) -> Locator:
        """The email field."""
        return self._page.get_by_role("textbox", name=LOGIN_EMAIL_NAME)

    @property
    def password_input(self) -> Locator:
        """The password field."""
        return self._page.get_by_role("textbox", name=LOGIN_PASSWORD_NAME)

    @property
    def login_button(self) -> Locator:
        """The button that submits the form."""
        return self._page.get_by_role("button", name=LOGIN_BUTTON_NAME, exact=True)

    @property
    def error_alert(self) -> Locator:
        """The alert shown when the credentials are refused."""
        return self._page.get_by_role("alert")
