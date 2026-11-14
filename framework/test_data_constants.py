"""Values the generated test data is built from."""

from __future__ import annotations

from framework.constants import DATA_PREFIX

TEST_FULL_NAME: str = f"{DATA_PREFIX}Sam Tester"
"""Owner of every generated address and card; the prefix lets cleanup find them."""

TEST_MOBILE_NUMBER: int = 5550100
TEST_ZIP_CODE: str = "10001"
TEST_STREET_TEMPLATE: str = "{token} Test Street"
"""A street unique per address, so a row can be found by it."""
TEST_CITY: str = "Testville"
TEST_STATE: str = "TS"
TEST_COUNTRY: str = "Testland"
TEST_CARD_NUMBER: int = 4111111111111111
"""The standard Visa test number; it is not a real card."""
TEST_CARD_EXPIRY_MONTH: int = 12
TEST_CARD_EXPIRY_YEAR: int = 2090
PASSWORD_TEMPLATE: str = "Sc-{token}-9a"
"""18 characters with mixed classes; the sign-up form allows 5 to 20."""
TOKEN_BYTES: int = 9
ANSWER_BYTES: int = 4
