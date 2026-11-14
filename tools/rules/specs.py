"""Rules for test modules: a test is its steps and nothing else."""

from __future__ import annotations

import ast

from tools.rules.context import FileContext, Violation, call_name, is_docstring, spec_functions

SUITE_MARKERS = frozenset({"bvt", "smoke", "api", "e2e"})
RAW_PAGE_CALLS = frozenset({"click", "fill", "type", "locator", "get_by_role", "get_by_test_id"})
STATE_READS = frozenset(
    {"is_visible", "is_enabled", "is_disabled", "is_checked", "text_content", "inner_text"}
)
SESSION_MODULE = "framework.helpers.session_cache"
SESSION_CALLS = frozenset({"restore_session", "save_session", "saved_session", "account_lock"})
SEED_CHANNELS = frozenset({"framework.helpers.api_client", "framework.helpers.cleanup"})
ALLOWED_MODULE_NAMES = frozenset({"pytestmark", "logger"})
MAX_LITERAL = 1


def check_spec(ctx: FileContext) -> list[Violation]:
    """T001, T003-T005, T008-T013, T015-T017 for both suites, S002 for BVT."""
    found = [*_module_level(ctx), *_imports(ctx)]
    for test in spec_functions(ctx.tree):
        found += _test_shape(ctx, test)
        found += _test_body(ctx, test)
    found += check_magic_integers(ctx)
    return found


def _module_level(ctx: FileContext) -> list[Violation]:
    helpers = [
        Violation(
            ctx.rel, n.lineno, "T003", f"helper {n.name}() in a spec; move it into the framework"
        )
        for n in ctx.tree.body
        if isinstance(n, ast.FunctionDef)
        and not n.name.startswith("test_")
        and not any(_is_fixture(d) for d in n.decorator_list)
    ]
    values = [
        Violation(ctx.rel, n.lineno, "T011", "module-level value; keep values in constants modules")
        for n in ctx.tree.body
        if isinstance(n, ast.Assign | ast.AnnAssign) and _assigned_names(n) - ALLOWED_MODULE_NAMES
    ]
    return helpers + values


def _assigned_names(node: ast.Assign | ast.AnnAssign) -> set[str]:
    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
    return {t.id for t in targets if isinstance(t, ast.Name)}


def _imports(ctx: FileContext) -> list[Violation]:
    found: list[Violation] = []
    for node in ast.walk(ctx.tree):
        line = getattr(node, "lineno", 1)
        for module in _imported_modules(node):
            found += _import_rules(ctx, line, module)
        if isinstance(node, ast.Call) and call_name(node) in SESSION_CALLS:
            message = "session handled in a spec; sign in through framework.helpers.sign_in"
            found.append(Violation(ctx.rel, node.lineno, "T015", message))
    return found


def _imported_modules(node: ast.AST) -> list[str]:
    """Every module an import statement brings in, in any spelling."""
    if isinstance(node, ast.Import):
        return [alias.name for alias in node.names]
    if isinstance(node, ast.ImportFrom) and node.module:
        return [node.module, *(f"{node.module}.{alias.name}" for alias in node.names)]
    return []


def _import_rules(ctx: FileContext, line: int, module: str) -> list[Violation]:
    found: list[Violation] = []
    if module.startswith("framework.locators"):
        found.append(Violation(ctx.rel, line, "T004", "locator import in a spec"))
    if module == SESSION_MODULE:
        message = "sessions imported in a spec; sign in through framework.helpers.sign_in"
        found.append(Violation(ctx.rel, line, "T015", message))
    if module in SEED_CHANNELS:
        message = f"seeding channel {module} in a spec; seed through the seeder"
        found.append(Violation(ctx.rel, line, "T016", message))
    return found


def _test_shape(ctx: FileContext, test: ast.FunctionDef) -> list[Violation]:
    found: list[Violation] = []
    markers = {_marker_name(d) for d in test.decorator_list} | _module_markers(ctx.tree)
    if not markers & SUITE_MARKERS:
        message = f"{test.name}() has no suite marker ({', '.join(sorted(SUITE_MARKERS))})"
        found.append(Violation(ctx.rel, test.lineno, "T005", message))
    if ast.get_docstring(test) is None:
        found.append(Violation(ctx.rel, test.lineno, "T008", f"{test.name}() has no docstring"))
    if test.returns is None:
        found.append(Violation(ctx.rel, test.lineno, "T009", f"{test.name}() is not -> None"))
    body = [s for s in test.body if not is_docstring(s)]
    if 0 < len(body) <= 2 and all(
        isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) for s in body
    ):
        message = f"{test.name}() delegates its whole body; write the steps here"
        found.append(Violation(ctx.rel, test.lineno, "T010", message))
    return found


def _test_body(ctx: FileContext, test: ast.FunctionDef) -> list[Violation]:
    found: list[Violation] = []
    for node in ast.walk(test):
        if isinstance(node, ast.For | ast.AsyncFor | ast.While):
            message = f"loop in {test.name}(); parametrize or use a collection method"
            found.append(Violation(ctx.rel, node.lineno, "T017", message))
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        if name == "expect":
            found.append(Violation(ctx.rel, node.lineno, "T001", "expect() in a spec"))
        if name in RAW_PAGE_CALLS and _on_page(node):
            message = f"raw page.{name}() in a spec; call a page object"
            found.append(Violation(ctx.rel, node.lineno, "T012", message))
        if name in STATE_READS:
            message = f".{name}() read in a spec; assert through an assertions class"
            found.append(Violation(ctx.rel, node.lineno, "T013", message))
    return found


def check_magic_integers(ctx: FileContext) -> list[Violation]:
    """S002: no integer above 1 as a call argument outside constants and decorators."""
    decorators = {
        id(n)
        for f in ast.walk(ctx.tree)
        if isinstance(f, ast.FunctionDef | ast.ClassDef)
        for d in f.decorator_list
        for n in ast.walk(d)
    }
    arguments = [
        value
        for node in ast.walk(ctx.tree)
        if isinstance(node, ast.Call) and id(node) not in decorators
        for value in [*node.args, *(k.value for k in node.keywords)]
    ]
    return [
        Violation(ctx.rel, v.lineno, "S002", f"integer {v.value} passed inline; name it")
        for v in arguments
        if isinstance(v, ast.Constant) and type(v.value) is int and v.value > MAX_LITERAL
    ]


def _on_page(node: ast.Call) -> bool:
    func = node.func
    return isinstance(func, ast.Attribute) and getattr(func.value, "id", "") == "page"


def _is_fixture(decorator: ast.expr) -> bool:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return isinstance(target, ast.Attribute) and target.attr == "fixture"


def _marker_name(decorator: ast.expr) -> str:
    target = decorator.func if isinstance(decorator, ast.Call) else decorator
    return target.attr if isinstance(target, ast.Attribute) else ""


def _module_markers(tree: ast.Module) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", "") == "pytestmark" for t in node.targets
        ):
            return {_marker_name(n) for n in ast.walk(node.value) if isinstance(n, ast.expr)}
    return set()
