"""Test case management, behind one small interface.

Tests never name a case. The mapping from test to case lives in
config/test_cases.toml, so cases can move without touching test code.

A reporter turns a run's results into what the case management system takes.
This showcase has no such system, so the only adapter is a dry run: it writes
the request it would have sent to a JSON file. A real adapter implements the
same `publish()` and is chosen in the config.
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol

CONFIG = Path("config/test_cases.toml")
PASSED, FAILED, SKIPPED = "passed", "failed", "skipped"
SEVERITY = {FAILED: 2, PASSED: 1, SKIPPED: 0}


def base_node_id(nodeid: str) -> str:
    """Drop parameters and the xdist group: `t.py::test_a[x]@g` -> `t.py::test_a`."""
    return re.sub(r"\[.*$|@.*$", "", nodeid)


@dataclass
class CaseResult:
    """One case's worst outcome over every test mapped to it."""

    case: str
    status: str
    tests: list[str] = field(default_factory=list)


@dataclass
class RunResults:
    """A run's results by case, and the tests no case claims."""

    title: str
    cases: dict[str, CaseResult] = field(default_factory=dict)
    unmapped: list[str] = field(default_factory=list)

    def add(self, case: str | None, nodeid: str, status: str) -> None:
        """Record one test's outcome under its case; the worst outcome wins."""
        if case is None:
            self.unmapped.append(nodeid)
            return
        result = self.cases.setdefault(case, CaseResult(case=case, status=status))
        result.tests.append(nodeid)
        if SEVERITY[status] > SEVERITY[result.status]:
            result.status = status


class CaseReporter(Protocol):
    """Publishes a run's results to a case management system."""

    def publish(self, results: RunResults) -> None:
        """Send the results."""


class DryRunReporter:
    """Writes the would-be request instead of sending it."""

    def __init__(self, output: Path) -> None:
        """Write to this file."""
        self.output = output

    def publish(self, results: RunResults) -> None:
        """Write the request a real adapter would send."""
        payload = {
            "adapter": "dry-run",
            "note": "Nothing was sent; this is the request a real adapter would make.",
            "request": {
                "method": "POST",
                "path": "/runs",
                "body": {
                    "title": results.title,
                    "results": [asdict(r) for r in results.cases.values()],
                },
            },
            "unmapped_tests": results.unmapped,
        }
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")


@dataclass(frozen=True)
class CaseMap:
    """The test-to-case mapping and the chosen adapter."""

    adapter: str
    cases: dict[str, str]

    @classmethod
    def load(cls, path: Path = CONFIG) -> CaseMap:
        """Read the mapping from the config file."""
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return cls(adapter=data["reporter"]["adapter"], cases=dict(data["cases"]))

    def case_for(self, nodeid: str) -> str | None:
        """The case a test reports to, or None."""
        return self.cases.get(base_node_id(nodeid))

    def tests_for(self, refs: set[str]) -> set[str]:
        """The tests mapped to any of these cases."""
        return {test for test, case in self.cases.items() if case in refs}

    def reporter(self, output: Path) -> CaseReporter:
        """The adapter the config chooses."""
        if self.adapter == "dry-run":
            return DryRunReporter(output)
        raise ValueError(f"unknown case reporter adapter {self.adapter!r}")


def parse_case_refs(text: str) -> set[str]:
    """Case refs from a box: separated by commas or spaces."""
    return {ref for ref in re.split(r"[,\s]+", text.strip()) if ref}
