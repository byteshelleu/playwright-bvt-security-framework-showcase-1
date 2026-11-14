"""Assertions on the address book."""

from __future__ import annotations

from playwright.sync_api import Page, expect

from framework.helpers.records import Address
from framework.locators.address_book_locators import AddressBookLocators


class AddressBookPageAssertions:
    """What the address book must show."""

    def __init__(self, page: Page) -> None:
        """Build the locators the assertions read."""
        self._page = page
        self.loc = AddressBookLocators(page)

    def loaded(self) -> None:
        """The address book is ready."""
        expect(self.loc.add_address_button).to_be_visible()

    def lists(self, address: Address) -> None:
        """The address is saved under its owner's name."""
        expect(self.loc.saved_address_row(address.street)).to_contain_text(address.full_name)
