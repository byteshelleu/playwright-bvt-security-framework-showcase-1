"""Run settings, read once from the environment.

Only a Juice Shop on this machine is a valid target: Docker locally, or the CI
service container that GitHub Actions also exposes on localhost. Any other
host is refused before a single request is sent.
"""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from urllib.parse import urlsplit

DEFAULT_URL = "http://localhost:3000"
LOCAL_HOSTS = frozenset({"localhost", "127.0.0.1", "::1"})
RUN_ID_LENGTH = 8


class TargetNotAllowedError(ValueError):
    """Raised when the configured URL points anywhere but this machine."""


def base_url() -> str:
    """The shop's address from JUICE_SHOP_URL; any host but this machine is refused."""
    url = os.environ.get("JUICE_SHOP_URL", DEFAULT_URL).rstrip("/")
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or parts.hostname not in LOCAL_HOSTS:
        raise TargetNotAllowedError(
            f"JUICE_SHOP_URL must point to Juice Shop on this machine, got {url!r}"
        )
    return url


def run_id() -> str:
    """One id per pytest run, shared by every xdist worker of that run."""
    shared = os.environ.get("PYTEST_XDIST_TESTRUNUID") or os.environ.get("RUN_ID")
    return (shared or secrets.token_hex(RUN_ID_LENGTH))[:RUN_ID_LENGTH]


def worker_id() -> str:
    """The xdist worker running this process, or main for a serial run."""
    return os.environ.get("PYTEST_XDIST_WORKER", "main")


@dataclass(frozen=True)
class Settings:
    """Where the shop runs, and which run and worker this process is."""

    base_url: str = field(default_factory=base_url)
    run_id: str = field(default_factory=run_id)
    worker: str = field(default_factory=worker_id)
