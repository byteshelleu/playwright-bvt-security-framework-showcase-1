"""Cleanup of what a run created, matched by the data prefix only.

Accounts are registered before anything is created for them. At teardown the
sweep removes what each registered account owns: its basket lines, and the
addresses and cards named with the prefix. It is idempotent: an account with
nothing left, or one it can no longer sign in as, is logged and skipped. The
shop cannot delete users; they go when the container restarts.
"""

from __future__ import annotations

import logging

from framework.constants import DATA_PREFIX, EMAIL_PREFIX
from framework.helpers.api_client import ApiClient, ApiError
from framework.helpers.records import Account, ApiSession

logger = logging.getLogger(__name__)


class CleanupRegistrar:
    """The accounts whose prefixed records a sweep removes."""

    def __init__(self, api: ApiClient) -> None:
        """Start with nothing registered."""
        self.api = api
        self._accounts: dict[str, Account] = {}

    def register(self, account: Account) -> None:
        """Register an account before anything is created for it."""
        if not account.email.startswith(EMAIL_PREFIX):
            raise ValueError(f"{account.label} is not a generated account; it is never cleaned")
        self._accounts[account.email] = account

    def sweep(self) -> None:
        """Remove every registered account's prefixed records."""
        for account in self._accounts.values():
            self._sweep_account(account)

    def _sweep_account(self, account: Account) -> None:
        try:
            session = self.api.login(account)
        except ApiError as error:
            logger.warning("cleanup skipped %s: %s", account.label, error)
            return
        self._remove_owned(session)

    def _remove_owned(self, session: ApiSession) -> None:
        for item_id in self.api.basket_item_ids(session):
            self.api.remove_basket_item(session, item_id)
        prefixed_addresses = [
            a.id for a in self.api.addresses(session) if a.fullName.startswith(DATA_PREFIX)
        ]
        for address_id in prefixed_addresses:
            self.api.remove_address(session, address_id)
        prefixed_cards = [
            c.id for c in self.api.cards(session) if c.fullName.startswith(DATA_PREFIX)
        ]
        for card_id in prefixed_cards:
            self.api.remove_card(session, card_id)
