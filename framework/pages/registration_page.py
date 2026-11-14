"""The registration page."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_REGISTER
from framework.helpers.records import Account
from framework.locators.registration_locators import RegistrationLocators
from framework.pages.registration_constants import SECURITY_QUESTION, SECURITY_QUESTIONS_API
from framework.pages.registration_page_assertions import RegistrationPageAssertions


class RegistrationPage:
    """Actions on the registration page."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = RegistrationLocators(page)
        self.assertions = RegistrationPageAssertions(page)

    def navigate(self) -> None:
        """Open the page once the security questions have arrived.

        The question list does not open while it has no options, so the page
        waits for the request that fills it.
        """
        with self.page.expect_response(SECURITY_QUESTIONS_API):
            self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_REGISTER))
        self.assertions.loaded()

    def register(self, account: Account) -> None:
        """Fill the sign-up form for the account and submit it."""
        self.loc.email_input.fill(account.email)
        self.loc.password_input.fill(account.password)
        self.loc.repeat_password_input.fill(account.password)
        self.loc.security_question_select.click()
        self.loc.security_question_option(SECURITY_QUESTION).click()
        self.loc.security_answer_input.fill(account.security_answer)
        self.loc.register_button.click()
