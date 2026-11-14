"""Values shared across the framework: timeouts, routes, storage keys, data prefix."""

from __future__ import annotations

EXPECT_TIMEOUT_MS: int = 10_000
"""How long an assertion waits before it fails."""

TIMEOUT_SHORT_MS: int = 2_000
"""How long a negative assertion waits, so a missing element fails fast."""

TEST_ID_ATTRIBUTE: str = "id"
"""Juice Shop marks its stable elements with id attributes, not data-testid."""

DATA_PREFIX: str = "SHOWCASE_"
"""Every record a run creates carries this prefix; cleanup matches it only."""

EMAIL_PREFIX: str = "showcase_"
"""The lower-case form of the prefix, which every generated email starts with."""

EMAIL_DOMAIN: str = "showcase.test"
"""A reserved domain, so a generated address can never reach a real inbox."""

APP_ROUTE_TEMPLATE: str = "/#/{route}"
"""The shop is a single-page app; every page is a route after the hash."""

ROUTE_LOGIN: str = "login"
ROUTE_REGISTER: str = "register"
ROUTE_SEARCH: str = "search"
ROUTE_BASKET: str = "basket"
ROUTE_ORDER_HISTORY: str = "order-history"
ROUTE_CHANGE_PASSWORD: str = "privacy-security/change-password"
ROUTE_ADDRESS_BOOK: str = "address/saved"

STORAGE_TOKEN_KEY: str = "token"
"""The localStorage key holding the signed-in user's token."""

SESSION_BASKET_KEY: str = "bid"
"""The sessionStorage key holding the signed-in user's basket id."""

BANNER_COOKIES: tuple[str, ...] = ("welcomebanner_status", "cookieconsent_status")
"""Cookies that keep the welcome and cookie banners closed."""

BANNER_DISMISSED: str = "dismiss"

XPATH_CARD_AROUND: str = "xpath=ancestor::mat-card[1]"  # noqa: R008
"""TIER 4: from an element up to the card holding it, which has no role."""

XPATH_ICON_BUTTON: str = "xpath=.//*[@data-icon='{icon}']/ancestor::button[1]"  # noqa: R008
"""TIER 4: from the icon an unnamed button draws, up to that button."""

ACCOUNT_FIXTURE_LABELS: tuple[str, ...] = ("shopper", "customer", "other_customer")
"""Accounts the fixture factory generates, one `<label>_account` fixture each."""

SESSION_LOCK_TIMEOUT_S: int = 60
"""How long a sign-in waits for another worker holding the same account's lock."""

PRICE_DECIMALS: int = 2
"""Prices are shown and compared to the cent."""

CURRENCY_SYMBOL: str = "¤"
"""The generic currency sign the shop prints after a price."""
