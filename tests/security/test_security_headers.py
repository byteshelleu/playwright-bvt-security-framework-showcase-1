"""Security: response headers on the shop's home page and API."""

from __future__ import annotations

import pytest

from framework.api_constants import HOME, SEARCH
from framework.security.asserts import (
    assert_header_equals,
    assert_header_not,
    assert_header_present,
)
from framework.security.client import SecurityClient
from framework.security.security_constants import (
    ALLOW_ORIGIN,
    ANY_ORIGIN,
    CONTENT_SECURITY_POLICY,
    CONTENT_TYPE_OPTIONS,
    FRAME_OPTIONS,
    NOSNIFF,
    SAME_ORIGIN,
)

pytestmark = pytest.mark.api


def test_headers_nosniff(security_client: SecurityClient) -> None:
    """Security: Browsers are told not to guess content types.

    Steps and expected results:
    1. Load the home page -> X-Content-Type-Options is nosniff.
    """
    response = security_client.get(HOME)

    assert_header_equals(response, CONTENT_TYPE_OPTIONS, NOSNIFF)


def test_headers_framing(security_client: SecurityClient) -> None:
    """Security: Only the shop itself may frame its pages.

    Steps and expected results:
    1. Load the home page -> X-Frame-Options is SAMEORIGIN.
    """
    response = security_client.get(HOME)

    assert_header_equals(response, FRAME_OPTIONS, SAME_ORIGIN)


def test_headers_content_security_policy(security_client: SecurityClient) -> None:
    """Security: The home page sets a Content-Security-Policy.

    Steps and expected results:
    1. Load the home page -> a Content-Security-Policy header is present.
    """
    response = security_client.get(HOME)

    assert_header_present(response, CONTENT_SECURITY_POLICY)


def test_headers_cors(security_client: SecurityClient) -> None:
    """Security: The API is not open to every origin.

    Steps and expected results:
    1. Call the search API -> Access-Control-Allow-Origin is not "*".
    """
    response = security_client.get(SEARCH)

    assert_header_not(response, ALLOW_ORIGIN, ANY_ORIGIN)
