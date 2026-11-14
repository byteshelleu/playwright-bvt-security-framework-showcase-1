"""Locators of the registration page."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.registration_constants import (
    REGISTER_BUTTON_NAME,
    REGISTER_EMAIL_NAME,
    REGISTER_PASSWORD_NAME,
    REGISTER_REPEAT_NAME,
    SECURITY_ANSWER_NAME,
    SECURITY_QUESTION_NAME,
)


class RegistrationLocators:
    """The sign-up form."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def email_input(self) -> Locator:
        """The email field."""
        return self._page.get_by_role("textbox", name=REGISTER_EMAIL_NAME)

    @property
    def password_input(self) -> Locator:
        """The password field."""
        return self._page.get_by_role("textbox", name=REGISTER_PASSWORD_NAME)

    @property
    def repeat_password_input(self) -> Locator:
        """The field that repeats the password."""
        return self._page.get_by_role("textbox", name=REGISTER_REPEAT_NAME)

    @property
    def security_question_select(self) -> Locator:
        """The list of security questions."""
        return self._page.get_by_role("combobox", name=SECURITY_QUESTION_NAME)

    def security_question_option(self, question: str) -> Locator:
        """One question in the opened list."""
        return self._page.get_by_role("option", name=question)

    @property
    def security_answer_input(self) -> Locator:
        """The answer to the chosen question."""
        return self._page.get_by_role("textbox", name=SECURITY_ANSWER_NAME)

    @property
    def register_button(self) -> Locator:
        """The button that submits the form."""
        return self._page.get_by_role("button", name=REGISTER_BUTTON_NAME)
