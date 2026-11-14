"""Retries cover infrastructure errors only, and every retry is reported."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

INNER_TESTS = """
from pathlib import Path

ATTEMPTS = Path("attempts")


def test_connection_drops_once():
    seen = int(ATTEMPTS.read_text()) if ATTEMPTS.exists() else 0
    ATTEMPTS.write_text(str(seen + 1))
    if seen == 0:
        raise ConnectionRefusedError("connect ECONNREFUSED 127.0.0.1:3000")


def test_wrong_result():
    assert 1 + 1 == 3
"""


def test_infrastructure_error_is_retried_and_reported(
    pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The dropped connection is retried once and listed; the wrong result is not retried."""
    pytester.makepyfile(test_inner=INNER_TESTS)
    monkeypatch.setenv("PYTHONPATH", str(REPO))
    result = pytester.runpytest_subprocess(
        "-p",
        "no:playwright",
        "-p",
        "framework.reporting.plugin",
        "--reruns=2",
        "--only-rerun=^ConnectionRefusedError:",
        "--flaky-report=flaky.json",
    )
    assert result.parseoutcomes() == {"passed": 1, "failed": 1, "rerun": 1}
    report = json.loads((pytester.path / "flaky.json").read_text())
    assert report["passed_after_retry"] == {"test_inner.py::test_connection_drops_once": 1}
