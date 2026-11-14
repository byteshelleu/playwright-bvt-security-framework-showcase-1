"""Run selection and retry reporting.

Options:
  --area NAME           run only the spec files of one CI area
  --cases REFS          run only the tests mapped to these cases; an unknown ref stops the run
  --flaky-report PATH   list the tests that passed only after a retry

Retries cover infrastructure errors only (see pyproject.toml), so a test on
the retry list points at the environment. The list is also printed in the
terminal summary and, in GitHub Actions, in the job summary.
"""

from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path

import pytest

from framework.ci_constants import AREA_SPEC_FILES
from framework.reporting.cases import PASSED, CaseMap, base_node_id, parse_case_refs

RERUN = "rerun"
"""The outcome pytest-rerunfailures gives each retried attempt."""


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the selection and reporting options."""
    group = parser.getgroup("showcase run")
    group.addoption("--area", choices=sorted(AREA_SPEC_FILES), help="run one CI area")
    group.addoption("--cases", default="", help="run only tests mapped to these cases")
    group.addoption("--flaky-report", type=Path, help="write tests that needed a retry here")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Keep only the selected area's files and the selected cases' tests."""
    area = config.getoption("area")
    refs = parse_case_refs(config.getoption("cases"))
    keep = list(items)
    if area:
        files = set(AREA_SPEC_FILES[area])
        keep = [item for item in keep if item.nodeid.split("::")[0] in files]
    if refs:
        case_map = CaseMap.load()
        unknown = refs - set(case_map.cases.values())
        if unknown:
            raise pytest.UsageError(f"unknown case refs: {sorted(unknown)}")
        wanted = case_map.tests_for(refs)
        keep = [item for item in keep if base_node_id(item.nodeid) in wanted]
    dropped = [item for item in items if item not in keep]
    if dropped:
        config.hook.pytest_deselected(items=dropped)
        items[:] = keep


def pytest_configure(config: pytest.Config) -> None:
    """Track retries on the process every worker reports to."""
    if not hasattr(config, "workerinput"):
        config.pluginmanager.register(RetryTracker(config), "showcase-retry-tracker")


class RetryTracker:
    """Counts retries and lists the tests that passed only after one."""

    def __init__(self, config: pytest.Config) -> None:
        """Read where to write the list."""
        self.output: Path | None = config.getoption("flaky_report")
        self.area: str = config.getoption("area") or "all"
        self.reruns: Counter[str] = Counter()
        self.passed: set[str] = set()

    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        """Count a retry, or remember a pass."""
        if str(report.outcome) == RERUN:
            self.reruns[base_node_id(report.nodeid)] += 1
        elif report.when == "call" and report.outcome == PASSED:
            self.passed.add(base_node_id(report.nodeid))

    def retried_then_passed(self) -> dict[str, int]:
        """Tests that passed after at least one retry, with their retry counts."""
        return {test: n for test, n in sorted(self.reruns.items()) if test in self.passed}

    def pytest_sessionfinish(self) -> None:
        """Write the list and the job summary."""
        if self.output is None:
            return
        self.output.parent.mkdir(parents=True, exist_ok=True)
        report = {"area": self.area, "passed_after_retry": self.retried_then_passed()}
        self.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
        summary = os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            lines = [f"### {self.area}: passed only after an infrastructure retry\n\n"]
            retried = self.retried_then_passed().items()
            lines += [f"- `{test}`: retried {n}x\n" for test, n in retried] or ["None.\n"]
            with Path(summary).open("a", encoding="utf-8") as file:
                file.writelines(lines)

    def pytest_terminal_summary(self, terminalreporter: pytest.TerminalReporter) -> None:
        """Print the list after the run."""
        if self.retried_then_passed():
            terminalreporter.section("passed only after an infrastructure retry")
            for test, count in self.retried_then_passed().items():
                terminalreporter.write_line(f"{test}: retried {count}x")
