"""Unit tests for the rule checker: each rule fires on a bad snippet, not on a good one."""

from __future__ import annotations

import ast

import pytest

from tools.rules.context import FileContext, apply_waivers
from tools.rules.duplicates import check_repeated_steps
from tools.rules.project import check_rerun_filter
from tools.rules_checker import check_file

STEPS = "".join(f"    page_object.step_{n}()\n" for n in range(6))


def rules(rel: str, source: str) -> set[str]:
    ctx = FileContext(rel=rel, source=source, tree=ast.parse(source))
    return {v.rule for v in apply_waivers(check_file(ctx), ctx.lines)}


@pytest.mark.parametrize(
    ("rel", "source", "rule"),
    [
        ("framework/x.py", "import time\ntime.sleep(1)\n", "R002"),
        ("framework/x.py", "page.wait_for_timeout(5)\n", "R002"),
        ("framework/x.py", "from typing import Optional\n", "R003"),
        ("framework/x.py", "page.get_by_text('a')\n", "R007"),
        ("framework/x.py", "page.locator('//div')\n", "R008"),
        ("framework/x.py", "page.locator('#id')\n", "R009"),
        ("framework/x.py", "print('x')\n", "R010"),
        ("framework/x.py", "page.goto('/', wait_until='networkidle')\n", "R011"),
        (
            "framework/pages/a_page.py",
            "class A:\n    def go(self):\n        self.loc.rows.first.click()\n",
            "R014",
        ),
        ("framework/x.py", "x = 1  # explain\n", "C010"),
        ("framework/x.py", "def f():\n    '''Fixed 2026-01-02 by hand.'''\n", "C011"),
        ("framework/x.py", "x = 1  # type: ignore\n", "S003"),
        (
            "tests/bvt/test_a.py",
            "def test_a(page) -> None:\n    '''Steps.'''\n    expect(page).to_be_ok()\n",
            "T001",
        ),
        ("tests/bvt/test_a.py", "def helper():\n    pass\n", "T003"),
        ("tests/bvt/test_a.py", "from framework.locators.a_locators import A\n", "T004"),
        ("tests/bvt/test_a.py", "def test_a() -> None:\n    '''Steps.'''\n    x = 1\n", "T005"),
        (
            "tests/bvt/test_a.py",
            "import pytest\n@pytest.mark.bvt\ndef test_a() -> None:\n    x = 1\n",
            "T008",
        ),
        ("tests/bvt/test_a.py", "VALUE = 3\n", "T011"),
        (
            "tests/bvt/test_a.py",
            "def test_a(page) -> None:\n    '''S.'''\n    page.click('a')\n    x = 1\n",
            "T012",
        ),
        (
            "tests/bvt/test_a.py",
            "from framework.helpers.session_cache import save_session\n",
            "T015",
        ),
        ("tests/bvt/test_a.py", "from framework.helpers.api_client import ApiClient\n", "T016"),
        (
            "tests/bvt/test_a.py",
            "def test_a(x) -> None:\n    '''S.'''\n    for i in x:\n        pass\n",
            "T017",
        ),
        (
            "tests/bvt/test_a.py",
            "def test_a(x) -> None:\n    '''S.'''\n    x.wait(5)\n    y = 1\n",
            "S002",
        ),
        (
            "framework/locators/a_locators.py",
            "class A:\n    def b(self):\n        '''B.'''\n",
            "L003",
        ),
        (
            "framework/locators/a_locators.py",
            "class A:\n    @property\n    def b(self) -> Locator:\n        return x\n",
            "L005",
        ),
        ("framework/locators/a_locators.py", "def f(loc):\n    loc.click()\n", "L001"),
        (
            "framework/pages/a_page.py",
            "class A:\n    def go(self) -> None:\n        '''Go.'''\n"
            "        self.page.get_by_role('x')\n",
            "P001",
        ),
        (
            "framework/pages/a_page.py",
            "class A:\n    def go(self) -> None:\n        pass\n",
            "P003",
        ),
        ("framework/pages/a_page.py", "def go(page):\n    expect(page).to_be_ok()\n", "P004"),
        ("framework/pages/a_page_assertions.py", "def ok(loc):\n    loc.fill('x')\n", "P005"),
        ("framework/helpers/a.py", "def go():\n    pass\n", "H002"),
        ("framework/helpers/a.py", "def go():\n    '''Go.'''\n", "H003"),
        ("framework/helpers/a.py", "CODE = '123456'\n", "H001"),
        ("tests/bvt/test_a.py", "CODE = '123456'\n", "T014"),
        ("framework/x.py", "loc.locator(XPATH_UP)\n", "R008"),
        ("framework/x.py", "page.goto('/rest/basket/1')\n", "R012"),
        ("framework/x.py", "PAIR = (NAMED, 'inline')\n", "S011"),
        ("tests/bvt/test_a.py", "from framework.helpers import api_client\n", "T016"),
        (
            "tests/bvt/test_a.py",
            "def test_a(x) -> None:\n    '''S.'''\n    restore_session(x, y)\n    z = 1\n",
            "T015",
        ),
        (
            "framework/x.py",
            "def assert_ok(x) -> None:\n    '''Ok.'''\n    x.check()\n",
            "A001",
        ),
    ],
)
def test_rule_fires(rel: str, source: str, rule: str) -> None:
    assert rule in rules(rel, source)


@pytest.mark.parametrize(
    ("rel", "source"),
    [
        ("framework/x.py", "page.get_by_role('button', name=NAME).click()\n"),
        ("framework/x.py", "LOCATOR = 'xpath=ancestor::div[1]'  # noqa: R008\n"),
        ("tests/unit/test_a.py", "def test_a():\n    assert [n for n in range(3)]\n"),
        (
            "framework/pages/a_page_assertions.py",
            "class A:\n    def ok(self) -> None:\n        '''Ok.'''\n"
            "        expect(self.loc.row).to_be_visible()\n",
        ),
    ],
)
def test_clean_code_passes(rel: str, source: str) -> None:
    assert rules(rel, source) == set()


def test_six_repeated_steps_are_flagged() -> None:
    one = f"def test_one(page_object) -> None:\n{STEPS}"
    source = f"{one}\n\n{one.replace('test_one', 'test_two')}"
    ctx = FileContext(rel="tests/bvt/test_a.py", source=source, tree=ast.parse(source))
    assert [v.rule for v in check_repeated_steps([ctx])] == ["T018"]


def test_rerun_filter_refuses_patterns_matching_test_failures() -> None:
    found = check_rerun_filter("pyproject.toml", ["--reruns=1", "--only-rerun=Error"])
    assert {v.rule for v in found} == {"C012"}
    assert len(found) == 2


def test_rerun_filter_accepts_infrastructure_patterns() -> None:
    patterns = ["--only-rerun=^ConnectionRefusedError:", "--only-rerun=^Error: [^\\n]*net::ERR_"]
    assert check_rerun_filter("pyproject.toml", patterns) == []


def test_rerun_filter_refuses_unanchored_patterns() -> None:
    found = check_rerun_filter("pyproject.toml", ["--only-rerun=net::ERR_"])
    assert [v.rule for v in found] == ["C012"]
