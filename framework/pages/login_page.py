"""The login page."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_LOGIN
from framework.locators.login_locators import LoginLocators
from framework.pages.login_page_assertions import LoginPageAssertions


class LoginPage:
    """Actions on the login page."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = LoginLocators(page)
        self.assertions = LoginPageAssertions(page)

    def navigate(self) -> None:
        """Open the login page and wait until the form is ready."""
        self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_LOGIN))
        self.assertions.loaded()

    def log_in(self, email: str, password: str) -> None:
        """Fill the form and submit it, whatever the outcome."""
        self.loc.email_input.fill(email)
        self.loc.password_input.fill(password)
        self.loc.login_button.click()
