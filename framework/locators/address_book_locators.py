"""Locators of the address book and its new address form."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from framework.pages.account_constants import (
    ADD_ADDRESS_NAME,
    MOBILE_FIELD,
    SUBMIT_ADDRESS_NAME,
)


class AddressBookLocators:
    """The saved addresses and the form that adds one."""

    def __init__(self, page: Page) -> None:
        """Keep the page the locators resolve on."""
        self._page = page

    @property
    def add_address_button(self) -> Locator:
        """The button that opens the new address form."""
        return self._page.get_by_role("button", name=ADD_ADDRESS_NAME)

    def form_input(self, field_name: str) -> Locator:
        """A text field of the new address form, by its label."""
        return self._page.get_by_role("textbox", name=field_name, exact=True)

    @property
    def mobile_input(self) -> Locator:
        """The mobile number field."""
        return self._page.get_by_role("spinbutton", name=MOBILE_FIELD)

    @property
    def submit_button(self) -> Locator:
        """The button that saves the address."""
        return self._page.get_by_role("button", name=SUBMIT_ADDRESS_NAME)

    def saved_address_row(self, street: str) -> Locator:
        """The row of the saved address on this street.

        SCOPE: has_text narrows the rows to the one holding the street.
        """
        return self._page.get_by_role("row").filter(has_text=street)
