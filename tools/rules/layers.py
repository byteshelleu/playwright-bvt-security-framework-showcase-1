"""Rules for the layers: locators, pages and components, helpers, conftest."""

from __future__ import annotations

import ast
from pathlib import Path

from tools.rules.context import FileContext, Violation, call_name
from tools.rules.specs import check_magic_integers

ACTIONS = frozenset(
    {
        "click",
        "dblclick",
        "fill",
        "check",
        "uncheck",
        "select_option",
        "press",
        "hover",
        "type",
        "goto",
        "set_input_files",
        "drag_to",
        "focus",
        "clear",
        "tap",
    }
)
GAP_MARKERS = ("BLOCKER", "TIER 3", "TIER 4")
TRACKER = Path("docs/locators-tracker.md")


def check_locators(ctx: FileContext) -> list[Violation]:
    """L001-L005, L010 and S004."""
    found: list[Violation] = []
    for node in ast.walk(ctx.tree):
        if isinstance(node, ast.Call) and call_name(node) in ACTIONS:
            rule = "L002" if call_name(node) == "goto" else "L001"
            found.append(
                Violation(ctx.rel, node.lineno, rule, f".{call_name(node)}() in a locator file")
            )
    for method in _public_methods(ctx.tree):
        found += _locator_method(ctx, method)
    return found


def _locator_method(ctx: FileContext, method: ast.FunctionDef) -> list[Violation]:
    found: list[Violation] = []
    is_property = any(getattr(d, "id", "") == "property" for d in method.decorator_list)
    returns = ast.unparse(method.returns) if method.returns else ""
    takes_data = len(method.args.args) > 1
    doc = ast.get_docstring(method) or ""
    if not is_property and not (takes_data and returns == "Locator"):
        message = f"{method.name}() is neither a @property nor a factory returning Locator"
        found.append(Violation(ctx.rel, method.lineno, "L003", message))
    if is_property and returns and returns != "Locator":
        found.append(Violation(ctx.rel, method.lineno, "L004", f"{method.name} returns {returns}"))
    if not doc:
        found.append(Violation(ctx.rel, method.lineno, "L005", f"{method.name} has no docstring"))
    if _filters_by_text(method) and not ("BLOCKER:" in doc or "SCOPE:" in doc):
        message = f"{method.name} filters by text without BLOCKER: or SCOPE: in its docstring"
        found.append(Violation(ctx.rel, method.lineno, "S004", message))
    if any(marker in doc for marker in GAP_MARKERS) and not _tracked(method.name):
        message = f"{method.name} is a locator gap with no row in {TRACKER}"
        found.append(Violation(ctx.rel, method.lineno, "L010", message))
    return found


def check_page_or_component(ctx: FileContext) -> list[Violation]:
    """P001-P005, P003 and S002."""
    found = check_magic_integers(ctx)
    for node in ast.walk(ctx.tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        on_page = _on_self_page(node)
        if on_page and name in {"get_by_role", "get_by_test_id"}:
            found.append(
                Violation(ctx.rel, node.lineno, "P001", f"inline {name}(); use the locators")
            )
        if on_page and name == "locator":
            found.append(
                Violation(ctx.rel, node.lineno, "P002", "inline locator(); use the locators")
            )
        if name == "expect" and not ctx.is_assertions:
            found.append(Violation(ctx.rel, node.lineno, "P004", "expect() in an action file"))
        if name in ACTIONS and ctx.is_assertions:
            found.append(
                Violation(ctx.rel, node.lineno, "P005", f".{name}() in an assertions file")
            )
    found += [
        Violation(ctx.rel, m.lineno, "P003", f"{m.name}() has no docstring")
        for m in _public_methods(ctx.tree)
        if ast.get_docstring(m) is None
    ]
    return found


def check_framework_code(ctx: FileContext) -> list[Violation]:
    """H002 and H003 on every public function and method; S002 where values are refused."""
    found = check_magic_integers(ctx) if ctx.holds_values_rule else []
    for node in _public_functions(ctx.tree):
        if ast.get_docstring(node) is None:
            found.append(Violation(ctx.rel, node.lineno, "H002", f"{node.name}() has no docstring"))
        if node.returns is None:
            message = f"{node.name}() has no return annotation"
            found.append(Violation(ctx.rel, node.lineno, "H003", message))
    return found


def check_assertion_helpers(ctx: FileContext) -> list[Violation]:
    """A001: an assertion helper asserts; one that never does always passes."""
    helpers = [
        f
        for f in _public_functions(ctx.tree)
        if f.name.startswith("assert_") or (ctx.is_assertions and f.name != "__init__")
    ]
    return [
        Violation(ctx.rel, f.lineno, "A001", f"{f.name}() never asserts")
        for f in helpers
        if not any(_asserts(n) for n in ast.walk(f))
    ]


def _asserts(node: ast.AST) -> bool:
    return isinstance(node, ast.Assert) or (
        isinstance(node, ast.Call) and call_name(node) == "expect"
    )


def _public_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    top = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    return [f for f in [*top, *_public_methods(tree)] if not f.name.startswith("_")]


def check_session_lock(path: Path) -> list[Violation]:
    """S005: the saved sessions are guarded by a file lock."""
    if path.is_file() and "from filelock import" not in path.read_text(encoding="utf-8"):
        return [Violation(str(path), 1, "S005", "saved sessions are written without a file lock")]
    return []


def check_conftest(ctx: FileContext) -> list[Violation]:
    """S009 and S010: the suite-wide expect timeout and base_url live in conftest."""
    calls = {call_name(n) for n in ast.walk(ctx.tree) if isinstance(n, ast.Call)}
    fixtures = {n.name for n in ast.walk(ctx.tree) if isinstance(n, ast.FunctionDef)}
    found: list[Violation] = []
    if ctx.rel == "tests/conftest.py" and "set_options" not in calls:
        found.append(Violation(ctx.rel, 1, "S009", "conftest does not call expect.set_options()"))
    if ctx.rel == "tests/conftest.py" and "base_url" not in fixtures:
        found.append(Violation(ctx.rel, 1, "S010", "conftest defines no base_url fixture"))
    return found


def _public_methods(tree: ast.Module) -> list[ast.FunctionDef]:
    return [
        m
        for c in tree.body
        if isinstance(c, ast.ClassDef)
        for m in c.body
        if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
    ]


def _filters_by_text(method: ast.FunctionDef) -> bool:
    return any(
        isinstance(n, ast.Call)
        and call_name(n) == "filter"
        and any(k.arg in {"has_text", "has_not_text"} for k in n.keywords)
        for n in ast.walk(method)
    )


def _on_self_page(node: ast.Call) -> bool:
    func = node.func
    if not isinstance(func, ast.Attribute):
        return False
    target = func.value
    return isinstance(target, ast.Attribute) and target.attr in {"page", "_page"}


def _tracked(name: str) -> bool:
    return TRACKER.is_file() and f"`{name}`" in TRACKER.read_text(encoding="utf-8")
