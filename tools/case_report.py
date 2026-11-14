"""Merge every area's JUnit file into one case report, sent through the adapter.

Usage: python -m tools.case_report OUTPUT JUNIT... [--expect AREA,...] [--cases REFS]

Nothing is published while an expected area has no JUnit file, a test has no
case, or a selected case has no result: a partial report would read as complete.
"""

from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from framework.reporting.cases import (
    FAILED,
    PASSED,
    SKIPPED,
    CaseMap,
    RunResults,
    parse_case_refs,
)


def junit_outcomes(junit: Path) -> list[tuple[str, str]]:
    """Each test's node id and final outcome in one JUnit file."""
    outcomes: list[tuple[str, str]] = []
    for case in ElementTree.parse(junit).getroot().iter("testcase"):
        module = case.get("classname", "").replace(".", "/")
        nodeid = f"{module}.py::{case.get('name', '')}"
        tags = {child.tag for child in case}
        status = FAILED if tags & {"failure", "error"} else SKIPPED if "skipped" in tags else PASSED
        outcomes.append((nodeid, status))
    return outcomes


def merged_results(junits: list[Path], case_map: CaseMap, title: str) -> RunResults:
    """Every test's outcome, grouped by case."""
    results = RunResults(title=title)
    for junit in junits:
        for nodeid, status in junit_outcomes(junit):
            results.add(case_map.case_for(nodeid), nodeid, status)
    return results


def missing(
    junits: list[Path], expect: list[str], refs: set[str], results: RunResults
) -> list[str]:
    """What the report lacks: expected areas without a file, selected cases without a result."""
    present = {junit.stem for junit in junits}
    gaps = [f"area {area}" for area in expect if area not in present]
    gaps += [f"case for test {test}" for test in results.unmapped]
    return gaps + [f"case {ref}" for ref in sorted(refs - set(results.cases))]


def main(arguments: list[str]) -> int:
    """Publish the merged report, or refuse with what is missing."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("output", type=Path)
    parser.add_argument("junits", type=Path, nargs="*")
    parser.add_argument("--expect", default="")
    parser.add_argument("--cases", default="")
    args = parser.parse_args(arguments)
    case_map, refs = CaseMap.load(), parse_case_refs(args.cases)
    junits = [j for j in args.junits if j.is_file()]
    title = f"Cases {', '.join(sorted(refs))}" if refs else "All areas"
    results = merged_results(junits, case_map, title)
    gaps = missing(junits, [a for a in args.expect.split(",") if a], refs, results)
    if gaps:
        sys.stderr.write(f"nothing published, missing: {', '.join(gaps)}\n")
        return 1
    case_map.reporter(args.output).publish(results)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
