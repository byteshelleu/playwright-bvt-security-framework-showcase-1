"""Security: secrets leaking through API responses."""

from __future__ import annotations

import pytest

from framework.api_constants import CHANGE_PASSWORD
from framework.helpers.records import ApiSession
from framework.security.asserts import assert_live, assert_no_fields
from framework.security.client import SecurityClient
from framework.security.probes import jwt_claims, own_user_route, unchanged_password
from framework.security.security_constants import SECRET_FIELDS

pytestmark = pytest.mark.api


def test_data_exposure_user_record(
    security_client: SecurityClient, customer_session: ApiSession
) -> None:
    """Security: The customer's own user record carries no secrets.

    Steps and expected results:
    1. Read the customer's own user record -> it is returned.
    2. Read its fields -> it holds no password hash or TOTP secret.
    """
    response = security_client.get(own_user_route(customer_session), customer_session)
    assert_live(response)

    assert_no_fields(response.json()["data"], SECRET_FIELDS)


def test_data_exposure_login_token(customer_session: ApiSession) -> None:
    """Security: The login token carries no secrets.

    Steps and expected results:
    1. Decode the token's payload, as anyone holding it can -> it holds no
       password hash or TOTP secret.
    """
    claims = jwt_claims(customer_session.token)

    assert_no_fields(claims["data"], SECRET_FIELDS)


def test_data_exposure_password_change(
    security_client: SecurityClient, customer_session: ApiSession
) -> None:
    """Security: Changing the password does not echo secrets back.

    Steps and expected results:
    1. Change the password to the same value -> it is accepted.
    2. Read the reply -> it holds no password hash or TOTP secret.
    """
    query = unchanged_password(customer_session.account.password)
    response = security_client.get(CHANGE_PASSWORD, customer_session, query)
    assert_live(response)

    assert_no_fields(response.json()["user"], SECRET_FIELDS)
