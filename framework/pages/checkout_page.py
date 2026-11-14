"""The checkout: address, delivery, payment and review screens."""

from __future__ import annotations

from playwright.sync_api import Page

from framework.helpers.records import Address, Card, DeliveryMethod
from framework.locators.checkout_locators import CheckoutLocators
from framework.pages.checkout_page_assertions import CheckoutPageAssertions


class CheckoutPage:
    """Actions on the checkout screens."""

    def __init__(self, page: Page) -> None:
        """Compose the locators and the assertions."""
        self.page = page
        self.loc = CheckoutLocators(page)
        self.assertions = CheckoutPageAssertions(page)

    def choose_address(self, address: Address) -> None:
        """Pick a saved address and continue."""
        self.loc.address_radio(address.street).check()
        self.loc.to_delivery_button.click()

    def choose_delivery(self, method: DeliveryMethod) -> None:
        """Pick a delivery speed and continue."""
        self.loc.delivery_radio(method.name).check()
        self.loc.to_payment_button.click()

    def choose_card(self, card: Card) -> None:
        """Pick a saved card and continue to the review."""
        self.loc.card_radio(card.last_four).check()
        self.loc.to_review_button.click()

    def place_order(self) -> None:
        """Place the order from the review."""
        self.loc.place_order_button.click()
