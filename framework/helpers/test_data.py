"""Generated test data: every name and email carries the run's prefix."""

from __future__ import annotations

import itertools
import secrets

from framework.config import run_id, worker_id
from framework.constants import EMAIL_DOMAIN, EMAIL_PREFIX
from framework.helpers.records import Account, Address, Card
from framework.test_data_constants import (
    ANSWER_BYTES,
    PASSWORD_TEMPLATE,
    TEST_CARD_EXPIRY_MONTH,
    TEST_CARD_EXPIRY_YEAR,
    TEST_CARD_NUMBER,
    TEST_CITY,
    TEST_COUNTRY,
    TEST_FULL_NAME,
    TEST_MOBILE_NUMBER,
    TEST_STATE,
    TEST_STREET_TEMPLATE,
    TEST_ZIP_CODE,
    TOKEN_BYTES,
)

_sequence = itertools.count(1)


def generate_account(label: str, *, reusable: bool = False) -> Account:
    """A new account whose email is unique to this run, worker and label."""
    email = f"{EMAIL_PREFIX}{run_id()}_{worker_id()}_{label}_{next(_sequence)}@{EMAIL_DOMAIN}"
    return Account(
        label=label,
        email=email,
        password=new_password(),
        security_answer=secrets.token_hex(ANSWER_BYTES),
        reusable=reusable,
    )


def new_password() -> str:
    """A new password the sign-up and change forms both accept."""
    return PASSWORD_TEMPLATE.format(token=secrets.token_urlsafe(TOKEN_BYTES))


def generate_address() -> Address:
    """A delivery address named with the data prefix."""
    return Address(
        full_name=TEST_FULL_NAME,
        mobile=TEST_MOBILE_NUMBER,
        zip_code=TEST_ZIP_CODE,
        street=TEST_STREET_TEMPLATE.format(token=secrets.token_hex(ANSWER_BYTES)),
        city=TEST_CITY,
        state=TEST_STATE,
        country=TEST_COUNTRY,
    )


def generate_card() -> Card:
    """A test card named with the data prefix."""
    return Card(
        full_name=TEST_FULL_NAME,
        number=TEST_CARD_NUMBER,
        exp_month=TEST_CARD_EXPIRY_MONTH,
        exp_year=TEST_CARD_EXPIRY_YEAR,
    )
