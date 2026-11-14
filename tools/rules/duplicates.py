"""T018: a block of steps is written once, then reused."""

from __future__ import annotations

import ast
from collections.abc import Iterator

from tools.rules.context import FileContext, Violation, is_docstring

WINDOW = 6


def check_repeated_steps(contexts: list[FileContext]) -> list[Violation]:
    """Flag six identical statements in a row that appear twice.

    Specs are compared test to test; pages, components and helpers compare
    every function, including two windows inside one function.
    """
    first_seen: dict[tuple[str, ...], tuple[str, str, int]] = {}
    repeats = (
        _first_repeat(ctx.rel, function, first_seen)
        for ctx in contexts
        for function in _functions(ctx)
    )
    return [violation for violation in repeats if violation is not None]


def _first_repeat(
    rel: str, function: ast.FunctionDef, first_seen: dict[tuple[str, ...], tuple[str, str, int]]
) -> Violation | None:
    repeat: Violation | None = None
    for line, window in _windows(function):
        origin = first_seen.setdefault(window, (rel, function.name, line))
        if repeat is None and (origin[0], origin[2]) != (rel, line):
            message = f"{function.name}() repeats steps from {origin[1]}() in {origin[0]}"
            repeat = Violation(rel, line, "T018", message)
    return repeat


def in_scope(ctx: FileContext) -> bool:
    """Files whose functions are compared: everything under test except unit tests."""
    in_tests = ctx.rel.startswith("tests/") and not ctx.rel.startswith("tests/unit/")
    return in_tests or ctx.is_page_or_component or ctx.is_helper or ctx.is_security_code


def _functions(ctx: FileContext) -> list[ast.FunctionDef]:
    functions = [n for n in ast.walk(ctx.tree) if isinstance(n, ast.FunctionDef)]
    if ctx.is_spec:
        return [f for f in functions if f.name.startswith("test_")]
    return functions


def _windows(function: ast.FunctionDef) -> Iterator[tuple[int, tuple[str, ...]]]:
    statements = [s for s in function.body if not is_docstring(s)]
    for start in range(len(statements) - WINDOW + 1):
        block = statements[start : start + WINDOW]
        yield block[0].lineno, tuple(ast.dump(s) for s in block)
