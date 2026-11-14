"""Security assertions: each raises with a message naming what was allowed or leaked."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from playwright.sync_api import APIResponse

from framework.security.security_constants import (
    OK_STATUS,
    SERVER_ERROR_FLOOR,
    TOO_MANY_REQUESTS,
)


def assert_live(response: APIResponse) -> None:
    """The route answers normally, so a refusal next to it is a real refusal."""
    assert response.status == OK_STATUS, f"{response.url} is not live: HTTP {response.status}"


def assert_refused(response: APIResponse, refusals: frozenset[int]) -> None:
    """Refused with one of exactly these statuses."""
    assert response.status in refusals, (
        f"{response.url} answered HTTP {response.status}, expected one of {sorted(refusals)}"
    )


def assert_header_equals(response: APIResponse, name: str, expected: str) -> None:
    """The header is present with the expected value."""
    actual = response.headers.get(name.lower(), "")
    assert actual.lower() == expected.lower(), f"{name} is {actual!r}, expected {expected!r}"


def assert_header_present(response: APIResponse, name: str) -> None:
    """The header is present."""
    assert name.lower() in response.headers, f"{name} is missing"


def assert_header_not(response: APIResponse, name: str, unsafe: str) -> None:
    """The header does not hold the unsafe value."""
    assert response.headers.get(name.lower()) != unsafe, f"{name} is {unsafe!r}"


def assert_no_fields(record: Mapping[str, Any], fields: Iterable[str]) -> None:
    """None of the secret fields is in the record."""
    exposed = sorted(set(fields) & set(record))
    assert not exposed, f"the response exposes {exposed}"


def assert_throttled(statuses: list[int]) -> None:
    """A burst of failed logins was answered with 429 at some point."""
    assert TOO_MANY_REQUESTS in statuses, (
        f"{len(statuses)} failed logins in a row were never throttled "
        f"(statuses {sorted(set(statuses))})"
    )


def assert_no_server_error(response: APIResponse) -> None:
    """The input did not crash the server."""
    assert response.status < SERVER_ERROR_FLOOR, (
        f"{response.url} crashed with HTTP {response.status}: {response.text()[:120]!r}"
    )


def assert_order_not_listed(order_id: str, response: APIResponse) -> None:
    """The order belongs to someone else and is not in this history."""
    listed = [order["orderId"] for order in response.json()["data"]]
    assert order_id not in listed, f"order {order_id} belongs to someone else but is listed"
