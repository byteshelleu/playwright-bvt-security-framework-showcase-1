"""Unit tests for the Juice Shop target guard; no network involved."""

from __future__ import annotations

import pytest

from framework.config import DEFAULT_URL, TargetNotAllowedError, base_url


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:3000",
        "http://127.0.0.1:3000/",
        "http://[::1]:3000",
        "https://localhost:8443",
    ],
)
def test_local_urls_are_accepted(monkeypatch: pytest.MonkeyPatch, url: str) -> None:
    monkeypatch.setenv("JUICE_SHOP_URL", url)
    assert base_url() == url.rstrip("/")


@pytest.mark.parametrize(
    "url",
    [
        "https://juice-shop.example.org",
        "http://localhost.example.org:3000",
        "http://10.0.0.5:3000",
        "ftp://localhost:3000",
        "localhost:3000",
    ],
)
def test_other_hosts_are_refused(monkeypatch: pytest.MonkeyPatch, url: str) -> None:
    monkeypatch.setenv("JUICE_SHOP_URL", url)
    with pytest.raises(TargetNotAllowedError):
        base_url()


def test_default_is_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JUICE_SHOP_URL", raising=False)
    assert base_url() == DEFAULT_URL
