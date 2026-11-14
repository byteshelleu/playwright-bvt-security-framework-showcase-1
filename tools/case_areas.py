"""The CI areas holding the given cases, for the workflow's area jobs.

Usage: python -m tools.case_areas "REFS"   prints ",area,area," (every area when REFS is empty)
An unknown case ref fails at once, before any area job starts.
"""

from __future__ import annotations

import sys

from framework.ci_constants import AREA_SPEC_FILES, CI_AREAS
from framework.reporting.cases import CaseMap, parse_case_refs


def areas_for(refs: set[str], case_map: CaseMap) -> list[str]:
    """The areas, in run order, whose spec files hold any of the cases."""
    if not refs:
        return list(CI_AREAS)
    unknown = refs - set(case_map.cases.values())
    if unknown:
        raise ValueError(f"unknown case refs: {sorted(unknown)}")
    files = {test.split("::")[0] for test in case_map.tests_for(refs)}
    return [area for area in CI_AREAS if files & set(AREA_SPEC_FILES[area])]


def main(arguments: list[str]) -> int:
    """Print the areas as ,a,b, so a workflow can test membership."""
    try:
        areas = areas_for(parse_case_refs(" ".join(arguments)), CaseMap.load())
    except ValueError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    sys.stdout.write(f",{','.join(areas)},\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
