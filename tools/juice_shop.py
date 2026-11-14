"""Juice Shop target: resolve its URL safely and check that it answers.

The suites may only run against a Juice Shop on this machine (Docker) or a CI
service container, which GitHub Actions also exposes on localhost. Any other
host is refused before a single request is sent.

Waiting for start-up happens elsewhere (the compose healthcheck locally, a
curl retry in CI); this tool only confirms the result.

Usage:
    python -m tools.juice_shop check   print the running version, or fail
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request

from framework.api_constants import APPLICATION_VERSION
from framework.config import TargetNotAllowedError, base_url


def fetch_version(url: str) -> str | None:
    """The running Juice Shop version, or None when it does not answer."""
    try:
        with urllib.request.urlopen(url + APPLICATION_VERSION, timeout=3) as response:
            return str(json.load(response)["version"])
    except (urllib.error.URLError, ConnectionError, TimeoutError, ValueError, KeyError):
        return None


def main(argv: list[str]) -> int:
    """Print the running version, or fail with why."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="print the running version, or fail")
    parser.parse_args(argv)
    try:
        url = base_url()
    except TargetNotAllowedError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    version = fetch_version(url)
    if version is None:
        sys.stderr.write(f"Juice Shop is not answering at {url}\n")
        return 1
    sys.stdout.write(f"Juice Shop {version} is ready at {url}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
