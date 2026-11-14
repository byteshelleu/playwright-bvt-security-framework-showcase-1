"""The address book and its new address form."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.constants import APP_ROUTE_TEMPLATE, ROUTE_ADDRESS_BOOK
from framework.helpers.records import Address
from framework.locators.address_book_locators import AddressBookLocators
from framework.pages.account_constants import (
    CITY_FIELD,
    COUNTRY_FIELD,
    NAME_FIELD,
    STATE_FIELD,
    STREET_FIELD,
    ZIP_FIELD,
)
from framework.pages.address_book_page_assertions import AddressBookPageAssertions


class AddressBookPage:
    """Actions on the address book."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = AddressBookLocators(page)
        self.assertions = AddressBookPageAssertions(page)

    def navigate(self) -> None:
        """Open the address book and wait until it is ready."""
        self.page.goto(APP_ROUTE_TEMPLATE.format(route=ROUTE_ADDRESS_BOOK))
        self.assertions.loaded()

    def add(self, address: Address) -> None:
        """Save a new address through the form."""
        self.loc.add_address_button.click()
        self.loc.form_input(COUNTRY_FIELD).fill(address.country)
        self.loc.form_input(NAME_FIELD).fill(address.full_name)
        self.loc.mobile_input.fill(str(address.mobile))
        self.loc.form_input(ZIP_FIELD).fill(address.zip_code)
        self.loc.form_input(STREET_FIELD).fill(address.street)
        self.loc.form_input(CITY_FIELD).fill(address.city)
        self.loc.form_input(STATE_FIELD).fill(address.state)
        self.loc.submit_button.click()
