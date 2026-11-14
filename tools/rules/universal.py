"""Rules every Python file follows."""

from __future__ import annotations

import ast
import io
import re
import tokenize

from tools.rules.context import FileContext, Violation, call_name, docstring_constant_ids

MAX_LINES = 400
MAX_NESTING = 2
LOCATOR_SHORTCUTS = {"get_by_label": "R005", "get_by_placeholder": "R006", "get_by_text": "R007"}
ACTIONS = frozenset(
    {"click", "fill", "type", "hover", "check", "uncheck", "select_option", "press"}
)
ROUTE_PREFIXES = ("/api/", "/rest/", "/#/")
SIX_DIGITS = re.compile(r"\d{6}")
ALLOWED_COMMENTS = ("noqa", "type:", "pragma", "!", "-*-")
NESTING_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try, ast.AsyncFor, ast.AsyncWith)
HISTORY = re.compile(
    "|".join(
        (
            r"\b(?:on|since|as of|until|adopted|added|fixed|verified|measured|confirmed|raised|"
            r"reported|changed|renamed|moved|seeded)\s+20\d{2}-\d{2}-\d{2}",
            r"\(20\d{2}-\d{2}-\d{2}\)",
            r"\([^()]*,\s*20\d{2}-\d{2}-\d{2}\)",
            r"\b(?:we|the user|user|client|team|PM|QA) (?:decided|agreed|ruled|asked|approved)\b",
            r"\bas agreed\b",
            r"\bat the user'?s (?:direction|request)\b",
            r"\bconfirmed by (?:the )?(?:user|client|QA|PM|team)\b",
            r"\bread on the live page\b",
            r"\bon the walk\b",
            r"\bheaded run\b",
            r"\bknown issue\b",
            r"\blive walk\b",
            r"\bmeasured live\b",
        )
    ),
    re.IGNORECASE,
)


def check_universal(ctx: FileContext) -> list[Violation]:
    """R001-R011, R014, S001, S003, C010 and C011."""
    found = [*_length(ctx), *_comments(ctx), *_history(ctx), *_nesting(ctx), *_collections(ctx)]
    docstrings = docstring_constant_ids(ctx.tree)
    for node in ast.walk(ctx.tree):
        found += _node_rules(ctx, node, docstrings)
    return found


def _node_rules(ctx: FileContext, node: ast.AST, docstrings: set[int]) -> list[Violation]:
    if isinstance(node, ast.Call):
        return _call_rules(ctx, node)
    if isinstance(node, ast.Subscript | ast.ImportFrom):
        return _typing_rules(ctx, node)
    if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
        return []
    if id(node) in docstrings or ctx.is_checker:
        return []
    return _string_rules(ctx, node)


def _length(ctx: FileContext) -> list[Violation]:
    if len(ctx.lines) <= MAX_LINES:
        return []
    message = f"{len(ctx.lines)} lines; split the file along a real boundary (max {MAX_LINES})"
    return [Violation(ctx.rel, MAX_LINES + 1, "R001", message)]


def _call_rules(ctx: FileContext, node: ast.Call) -> list[Violation]:
    name = call_name(node)
    found: list[Violation] = []
    func = node.func
    if (
        name == "sleep"
        and isinstance(func, ast.Attribute)
        and getattr(func.value, "id", "") == "time"
    ):
        found.append(Violation(ctx.rel, node.lineno, "R002", "time.sleep(); wait for a condition"))
    if name == "wait_for_timeout":
        found.append(
            Violation(ctx.rel, node.lineno, "R002", "wait_for_timeout(); wait for a condition")
        )
    if name in LOCATOR_SHORTCUTS:
        rule = LOCATOR_SHORTCUTS[name]
        found.append(Violation(ctx.rel, node.lineno, rule, f"{name}(); locate by role or test id"))
    if name == "locator" and _uses_xpath_constant(node):
        message = "Tier 4 XPath used without its waiver on this line"
        found.append(Violation(ctx.rel, node.lineno, "R008", message))
    if name == "print":
        found.append(Violation(ctx.rel, node.lineno, "R010", "print(); use logging"))
    if name in ACTIONS and (ctx.is_page_or_component or ctx.is_spec) and _acts_on_position(func):
        message = f".first/.nth() followed by .{name}(); locate the one element instead"
        found.append(Violation(ctx.rel, node.lineno, "R014", message))
    return found


def _uses_xpath_constant(node: ast.Call) -> bool:
    return any(isinstance(n, ast.Name) and n.id.startswith("XPATH_") for n in ast.walk(node))


def _acts_on_position(func: ast.expr) -> bool:
    if not isinstance(func, ast.Attribute):
        return False
    target = func.value
    if isinstance(target, ast.Attribute) and target.attr in {"first", "last"}:
        return True
    return isinstance(target, ast.Call) and call_name(target) == "nth"


def _string_rules(ctx: FileContext, node: ast.Constant) -> list[Violation]:
    text = str(node.value).strip()
    found: list[Violation] = []
    if text == "networkidle":
        found.append(Violation(ctx.rel, node.lineno, "R011", "networkidle wait"))
    if text.startswith(("//", "(//", "xpath=")):
        found.append(Violation(ctx.rel, node.lineno, "R008", "XPath outside the Tier 4 waiver"))
    if text.startswith(ROUTE_PREFIXES) and not ctx.is_constants:
        message = f"inline route {text!r}; use the constants module that spells it"
        found.append(Violation(ctx.rel, node.lineno, "R012", message))
    if SIX_DIGITS.fullmatch(text) and (ctx.is_spec or ctx.is_helper):
        rule = "T014" if ctx.is_spec else "H001"
        found.append(Violation(ctx.rel, node.lineno, rule, "hardcoded 6-digit code"))
    return found + _css_rule(ctx, node)


def _css_rule(ctx: FileContext, node: ast.Constant) -> list[Violation]:
    line = ctx.lines[node.lineno - 1] if node.lineno <= len(ctx.lines) else ""
    if re.search(r"\.locator\(\s*[\"'][.#\[]", line):
        return [Violation(ctx.rel, node.lineno, "R009", "CSS locator outside Tier 3")]
    return []


def _typing_rules(ctx: FileContext, node: ast.Subscript | ast.ImportFrom) -> list[Violation]:
    names: set[str] = set()
    if isinstance(node, ast.ImportFrom) and node.module == "typing":
        names = {alias.name for alias in node.names}
    elif isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
        names = {node.value.id}
    found: list[Violation] = []
    if "Optional" in names:
        found.append(Violation(ctx.rel, node.lineno, "R003", "Optional; write X | None"))
    if "Union" in names:
        found.append(Violation(ctx.rel, node.lineno, "R004", "Union; write X | Y"))
    return found


def _comments(ctx: FileContext) -> list[Violation]:
    found: list[Violation] = []
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(ctx.source).readline))
    except (tokenize.TokenError, SyntaxError):
        return found
    for token in tokens:
        if token.type != tokenize.COMMENT:
            continue
        body = token.string.lstrip("#").strip()
        if body.startswith("type: ignore") and "[" not in body:
            found.append(Violation(ctx.rel, token.start[0], "S003", "type: ignore without a code"))
        if not body.startswith(ALLOWED_COMMENTS) and not token.string.startswith("#!"):
            message = "# comment; explain in the docstring"
            found.append(Violation(ctx.rel, token.start[0], "C010", message))
    return found


def _history(ctx: FileContext) -> list[Violation]:
    owners = [
        ctx.tree,
        *(n for n in ast.walk(ctx.tree) if isinstance(n, ast.FunctionDef | ast.ClassDef)),
    ]
    found: list[Violation] = []
    for owner in owners:
        doc = ast.get_docstring(owner, clean=False)
        match = HISTORY.search(doc or "")
        if match:
            line = owner.body[0].lineno if owner.body else 1
            message = f"docstring records history ({match.group(0)!r}); describe the code"
            found.append(Violation(ctx.rel, line, "C011", message))
    return found


def _nesting(ctx: FileContext) -> list[Violation]:
    found: list[Violation] = []
    for node in ast.walk(ctx.tree):
        if isinstance(node, ast.FunctionDef) and _depth(node) > MAX_NESTING:
            message = f"{node.name}() nests control flow deeper than {MAX_NESTING}"
            found.append(Violation(ctx.rel, node.lineno, "S001", message))
    return found


def _depth(node: ast.AST, level: int = 0) -> int:
    deepest = level
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef):
            continue
        inner = level + 1 if isinstance(child, NESTING_NODES) else level
        deepest = max(deepest, _depth(child, inner))
    return deepest


def _collections(ctx: FileContext) -> list[Violation]:
    """S011: a module-level collection is all named constants or all inline literals."""
    found: list[Violation] = []
    for node in ctx.tree.body:
        value = node.value if isinstance(node, ast.Assign | ast.AnnAssign) else None
        if isinstance(value, ast.Tuple | ast.List | ast.Set) and _mixes(value.elts):
            message = "collection mixes named constants and inline values"
            found.append(Violation(ctx.rel, node.lineno, "S011", message))
    return found


def _mixes(members: list[ast.expr]) -> bool:
    named = any(isinstance(m, ast.Name) for m in members)
    inline = any(isinstance(m, ast.Constant) and isinstance(m.value, str) for m in members)
    return named and inline
