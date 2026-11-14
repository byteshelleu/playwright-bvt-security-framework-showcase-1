"""The one entry point for test data.

Every method takes the same four steps, in order: it refuses an account the
run did not generate, registers cleanup before creating, creates through the
API as that account, and returns a typed record.
"""

from __future__ import annotations

import dataclasses

from framework.constants import PRICE_DECIMALS
from framework.helpers.api_client import ApiClient
from framework.helpers.cleanup import CleanupRegistrar
from framework.helpers.records import (
    Account,
    Address,
    ApiSession,
    Card,
    DeliveryMethod,
    Product,
    SeededBasket,
    SeededOrder,
)
from framework.helpers.test_data import generate_account, generate_address, generate_card


class Seeder:
    """Creates the preconditions a test needs."""

    def __init__(self, api: ApiClient, registrar: CleanupRegistrar) -> None:
        """Seed through the API client; register cleanup with the registrar."""
        self.api = api
        self.registrar = registrar
        self._sessions: dict[str, ApiSession] = {}

    def account(self, label: str) -> Account:
        """A new account, never saved as a session, for a case that changes it."""
        account = generate_account(label)
        self.registrar.register(account)
        self.api.register(account)
        return account

    def reuse(self, account: Account) -> Account:
        """A shared fixture account, swept after the test so the next one starts clean."""
        self.registrar.register(account)
        return account

    def address(self, account: Account) -> Address:
        """A saved address for the account."""
        session = self._session_for(account)
        address = generate_address()
        return dataclasses.replace(address, id=self.api.add_address(session, address))

    def card(self, account: Account) -> Card:
        """A saved test card for the account."""
        session = self._session_for(account)
        card = generate_card()
        return dataclasses.replace(card, id=self.api.add_card(session, card))

    def basket(self, account: Account, *products: Product) -> SeededBasket:
        """Products in the account's basket, one of each."""
        session = self._session_for(account)
        item_ids = tuple(self.api.add_to_basket(session, product) for product in products)
        return SeededBasket(item_ids=item_ids)

    def order(self, account: Account, product: Product, delivery: DeliveryMethod) -> SeededOrder:
        """A placed order of one product, with a new address and card."""
        self.basket(account, product)
        address, card = self.address(account), self.card(account)
        if address.id is None or card.id is None:
            raise ValueError("a seeded address or card came back without an id")
        session = self._session_for(account)
        order_id = self.api.checkout(session, address.id, card.id, delivery)
        return SeededOrder(
            order_id=order_id, total=round(product.price + delivery.price, PRICE_DECIMALS)
        )

    def _session_for(self, account: Account) -> ApiSession:
        self.registrar.register(account)
        if account.email not in self._sessions:
            self._sessions[account.email] = self.api.login(account)
        return self._sessions[account.email]
