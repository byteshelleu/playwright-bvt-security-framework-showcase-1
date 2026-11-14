"""What a check needs to know about a file, and how findings are reported."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

SPEC_DIRS = ("tests/bvt/", "tests/security/")
BVT_DIR = "tests/bvt/"
NOQA_RE = re.compile(r"#\s*noqa:\s*([A-Z0-9, ]+)")


@dataclass(frozen=True)
class Violation:
    """One broken rule at one line of one file."""

    path: str
    line: int
    rule: str
    message: str

    def __str__(self) -> str:
        """Render as `path:line: RULE message`."""
        return f"{self.path}:{self.line}: {self.rule} {self.message}"


@dataclass
class FileContext:
    """A parsed Python file and the scopes it belongs to."""

    rel: str
    source: str
    tree: ast.Module
    lines: list[str] = field(init=False)
    name: str = field(init=False)

    def __post_init__(self) -> None:
        """Derive the file name and its lines."""
        self.lines = self.source.splitlines()
        self.name = Path(self.rel).name

    @property
    def is_checker(self) -> bool:
        """The rule checker and its tests, which spell out the patterns they refuse."""
        return self.rel.startswith("tools/rules/") or self.name.startswith("test_rules_")

    @property
    def is_spec(self) -> bool:
        """A test module of either suite."""
        return self.rel.startswith(SPEC_DIRS) and self.name.startswith("test_")

    @property
    def is_bvt_spec(self) -> bool:
        """A test module of the BVT suite."""
        return self.rel.startswith(BVT_DIR) and self.name.startswith("test_")

    @property
    def is_locator(self) -> bool:
        """A locator module."""
        return self.rel.startswith("framework/locators/") and self.name.endswith("_locators.py")

    @property
    def is_constants(self) -> bool:
        """A constants module, the one place values live."""
        return self.name.endswith("constants.py")

    @property
    def is_page_or_component(self) -> bool:
        """A page object, a component, or an assertions sibling of either."""
        in_layer = self.rel.startswith(("framework/pages/", "framework/components/"))
        return in_layer and self.name != "__init__.py" and not self.is_constants

    @property
    def is_assertions(self) -> bool:
        """An assertions sibling of a page or component."""
        return self.is_page_or_component and self.name.endswith("_assertions.py")

    @property
    def is_helper(self) -> bool:
        """A helper module."""
        return self.rel.startswith("framework/helpers/") and self.name != "__init__.py"

    @property
    def is_framework_code(self) -> bool:
        """Framework and tool modules outside the layers with rules of their own."""
        in_scope = self.rel.startswith(("framework/", "tools/"))
        layered = self.is_locator or self.is_page_or_component
        return in_scope and not layered and self.name != "__init__.py"

    @property
    def is_security_code(self) -> bool:
        """The security suite's framework modules."""
        return self.rel.startswith("framework/security/") and not self.is_constants

    @property
    def is_conftest(self) -> bool:
        """A pytest conftest module."""
        return self.name == "conftest.py"

    @property
    def holds_values_rule(self) -> bool:
        """Files where magic integers are refused (S002)."""
        holds = self.is_spec or self.is_page_or_component or self.is_helper or self.is_security_code
        return holds and not self.is_constants


def suppressed(line: str, rule: str) -> bool:
    """Whether the line waives the rule with `# noqa: RULE`."""
    match = NOQA_RE.search(line)
    if match is None:
        return False
    return rule in {r.strip() for r in match.group(1).split(",")}


def apply_waivers(violations: list[Violation], lines: list[str]) -> list[Violation]:
    """Drop violations waived on their own line."""
    return [
        v
        for v in violations
        if not (0 < v.line <= len(lines) and suppressed(lines[v.line - 1], v.rule))
    ]


def call_name(node: ast.Call) -> str:
    """The called attribute or function name."""
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return ""


def is_docstring(statement: ast.stmt) -> bool:
    """A bare string statement."""
    return isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant)


def spec_functions(tree: ast.Module) -> list[ast.FunctionDef]:
    """Every function named test_*."""
    return [
        n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
    ]


def docstring_constant_ids(tree: ast.AST) -> set[int]:
    """Ids of the string nodes that are docstrings."""
    owners = [tree, *(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef)))]
    found: set[int] = set()
    for owner in owners:
        body = getattr(owner, "body", [])
        if body and is_docstring(body[0]):
            found.add(id(body[0].value))
    return found
