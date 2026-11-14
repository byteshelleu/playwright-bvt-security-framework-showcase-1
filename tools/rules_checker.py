"""Run every rule over the repository and print the violations.

Usage: python -m tools.rules_checker [PATH ...]   (default: the whole repository)
A justified exemption goes on the offending line as `# noqa: RULE`.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from framework.ci_constants import CI_AREAS
from tools.rules.context import FileContext, Violation, apply_waivers
from tools.rules.duplicates import check_repeated_steps, in_scope
from tools.rules.layers import (
    check_assertion_helpers,
    check_conftest,
    check_framework_code,
    check_locators,
    check_page_or_component,
    check_session_lock,
)
from tools.rules.project import check_pyproject, check_workflows
from tools.rules.specs import check_spec
from tools.rules.universal import check_universal

ROOTS = ("framework", "tests", "tools")
SESSION_CACHE = Path("framework/helpers/session_cache.py")


def check_file(ctx: FileContext) -> list[Violation]:
    """Every rule whose scope covers the file."""
    found = check_universal(ctx)
    if ctx.is_spec:
        found += check_spec(ctx)
    if ctx.is_locator:
        found += check_locators(ctx)
    if ctx.is_page_or_component:
        found += check_page_or_component(ctx)
    if ctx.is_framework_code:
        found += check_framework_code(ctx)
    found += check_assertion_helpers(ctx)
    if ctx.is_conftest:
        found += check_conftest(ctx)
    return found


def check_repository(paths: list[Path]) -> list[Violation]:
    """Per-file rules, repeated steps, and the project configuration."""
    contexts = [_parse(p) for p in paths]
    found: list[Violation] = []
    for ctx in contexts:
        found += apply_waivers(check_file(ctx), ctx.lines)
    found += check_repeated_steps([c for c in contexts if in_scope(c)])
    project = check_pyproject(Path("pyproject.toml")) + check_workflows(CI_AREAS)
    return found + project + check_session_lock(SESSION_CACHE)


def python_files(arguments: list[str]) -> list[Path]:
    """The files named, or every Python file under the source roots."""
    if arguments:
        return [Path(a) for a in arguments if a.endswith(".py")]
    return sorted(p for root in ROOTS for p in Path(root).rglob("*.py"))


def main(arguments: list[str]) -> int:
    """Print violations; exit 1 when there are any."""
    violations = check_repository(python_files(arguments))
    sys.stderr.writelines(f"{v}\n" for v in violations)
    return 1 if violations else 0


def _parse(path: Path) -> FileContext:
    source = path.read_text(encoding="utf-8")
    return FileContext(rel=path.as_posix(), source=source, tree=ast.parse(source))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
