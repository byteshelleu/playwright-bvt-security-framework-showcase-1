"""Rules for project configuration: pyproject.toml and the CI workflows."""

from __future__ import annotations

import itertools
import re
import tomllib
from pathlib import Path

from tools.rules.context import Violation

REQUIRED_ADDOPTS = {
    "C001": "--screenshot=only-on-failure",
    "C002": "--tracing=retain-on-failure",
    "C003": "--output=test-results",
}
REQUIRED_PACKAGES = {
    "C004": "pytest-rerunfailures",
    "C005": "pytest-xdist",
    "C006": "filelock",
    "C007": "pytest-html",
}
TEST_FAILURES = (
    "AssertionError: Locator expected to be visible",
    "AssertionError: the page reported net::ERR_ABORTED",
    "AssertionError: the body mentions ECONNREFUSED and ConnectionRefusedError:",
    "TimeoutError: Locator.click: Timeout 30000ms exceeded.",
    "TimeoutError: Page.goto: Timeout 30000ms exceeded. net::ERR_ABORTED",
)
"""How pytest-rerunfailures sees a wrong result: `<ExceptionName>: <message>`.
A retry pattern that matches any of them would retry a test failure."""
AREA_WORKFLOW = Path(".github/workflows/area.yml")
TESTS_WORKFLOW = Path(".github/workflows/tests.yml")


def check_pyproject(path: Path) -> list[Violation]:
    """C001-C007, C009 and C012."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    addopts: list[str] = data["tool"]["pytest"]["ini_options"].get("addopts", [])
    found = [
        Violation(str(path), 1, rule, f"addopts lacks {option}")
        for rule, option in REQUIRED_ADDOPTS.items()
        if option not in addopts
    ]
    packages = " ".join(data.get("dependency-groups", {}).get("dev", []))
    found += [
        Violation(str(path), 1, rule, f"{package} is not a dependency")
        for rule, package in REQUIRED_PACKAGES.items()
        if package not in packages
    ]
    if not (path.parent / "uv.lock").is_file():
        found.append(Violation(str(path), 1, "C009", "uv.lock is missing"))
    return found + check_rerun_filter(str(path), addopts)


def check_rerun_filter(where: str, addopts: list[str]) -> list[Violation]:
    """C012: retries are opted in by CI, and only infrastructure errors match."""
    found: list[Violation] = []
    if any(o.startswith(("--reruns", "--rerun-except")) for o in addopts):
        found.append(Violation(where, 1, "C012", "addopts sets retries; CI passes --reruns"))
    patterns = [o.split("=", 1)[1] for o in addopts if o.startswith("--only-rerun=")]
    if not patterns:
        found.append(Violation(where, 1, "C012", "no --only-rerun pattern"))
    for pattern in patterns:
        try:
            compiled = re.compile(pattern)
        except re.error:
            found.append(Violation(where, 1, "C012", f"--only-rerun {pattern!r} does not compile"))
            continue
        if any(compiled.search(failure) for failure in TEST_FAILURES):
            message = f"--only-rerun {pattern!r} matches a test failure"
            found.append(Violation(where, 1, "C012", message))
    return found


def check_workflows(areas: tuple[str, ...]) -> list[Violation]:
    """CI001-CI003 on the area workflow, CI005 on the tests workflow."""
    found: list[Violation] = []
    area = AREA_WORKFLOW.read_text(encoding="utf-8") if AREA_WORKFLOW.is_file() else ""
    where = str(AREA_WORKFLOW)
    if "upload-artifact" not in area or "test-results" not in area:
        found.append(Violation(where, 1, "CI001", "results are not uploaded from test-results"))
    if "--reruns" not in area:
        found.append(Violation(where, 1, "CI002", "pytest runs without --reruns"))
    if "--junitxml" not in area:
        found.append(Violation(where, 1, "CI003", "pytest runs without --junitxml"))
    return found + check_area_chain(areas)


def check_area_chain(areas: tuple[str, ...]) -> list[Violation]:
    """CI005: one job per area, in order, each after the one before, red or green."""
    tests = TESTS_WORKFLOW.read_text(encoding="utf-8") if TESTS_WORKFLOW.is_file() else ""
    where = str(TESTS_WORKFLOW)
    blocks = dict(re.findall(r"^  ([a-z][a-z0-9_-]*):\n((?:    .*\n|\n)*)", tests, re.MULTILINE))
    area_jobs = tuple(job for job in blocks if job in areas)
    found: list[Violation] = []
    if area_jobs != areas:
        found.append(Violation(where, 1, "CI005", f"area jobs {area_jobs} differ from {areas}"))
    if "matrix:" in tests:
        found.append(Violation(where, 1, "CI005", "area jobs run as a matrix"))
    for previous, job in itertools.pairwise(areas):
        block = blocks.get(job, "")
        if previous not in block.split("if:")[0] or "!cancelled()" not in block:
            message = f"{job} does not run after {previous} whatever it concluded"
            found.append(Violation(where, 1, "CI005", message))
    return found
