"""Security suite fixtures and hooks.

A security test is never retried: a pass on a second try is itself a finding.
Every security item is pinned to zero retries, whatever --reruns says, and a
flaky marker is refused. Every failed probe is written to a findings file,
which CI uploads with the results.
"""

from __future__ import annotations

import json

import pytest
from playwright.sync_api import APIRequestContext

from framework.helpers.api_client import ApiClient
from framework.helpers.records import Account, ApiSession
from framework.security.client import SecurityClient
from framework.security.security_constants import (
    FINDING_TEXT_LIMIT,
    FINDINGS_FILE,
    SECURITY_TESTS_DIR,
)

_findings: list[dict[str, str]] = []


@pytest.fixture(scope="session")
def security_client(api_request: APIRequestContext) -> SecurityClient:
    """The client every probe is sent through."""
    return SecurityClient(api_request)


@pytest.fixture(scope="session")
def customer_session(api_client: ApiClient, customer_account: Account) -> ApiSession:
    """The probing customer, signed in through the API."""
    return api_client.login(customer_account)


@pytest.fixture(scope="session")
def other_customer_session(api_client: ApiClient, other_customer_account: Account) -> ApiSession:
    """A second customer, whose data the first one must not reach."""
    return api_client.login(other_customer_account)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Refuse a flaky marker and pin every security test to zero retries."""
    security = [item for item in items if item.nodeid.startswith(SECURITY_TESTS_DIR)]
    flaky = [item.nodeid for item in security if item.get_closest_marker("flaky")]
    if flaky:
        raise pytest.UsageError(f"security tests are never retried: {flaky}")
    for item in security:
        item.add_marker(pytest.mark.flaky(reruns=0))


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Record every failed security probe."""
    is_security = report.nodeid.startswith(SECURITY_TESTS_DIR)
    if is_security and report.when == "call" and report.failed:
        message = str(report.longrepr)[-FINDING_TEXT_LIMIT:]
        _findings.append({"test": report.nodeid, "message": message})


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Write the findings once, where every worker's results arrive."""
    if _findings and not hasattr(session.config, "workerinput"):
        FINDINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        FINDINGS_FILE.write_text(json.dumps(_findings, indent=2), encoding="utf-8")
