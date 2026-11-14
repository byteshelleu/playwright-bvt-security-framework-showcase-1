"""Unit tests for the case reporter, the case selection and the merged report."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from framework.ci_constants import AREA_SPEC_FILES
from framework.reporting.cases import (
    FAILED,
    PASSED,
    CaseMap,
    DryRunReporter,
    RunResults,
    base_node_id,
    parse_case_refs,
)
from tools.case_areas import areas_for
from tools.case_report import main as case_report

JUNIT = """<testsuites><testsuite>
<testcase classname="tests.bvt.test_basket" name="test_basket_add_product[chromium]"/>
<testcase classname="tests.security.test_authorization"
 name="test_authorization_token_required[/api/Users]"/>
<testcase classname="tests.security.test_authorization"
 name="test_authorization_token_required[/rest/order-history]">
<failure message="x"/></testcase>
</testsuite></testsuites>"""


def test_base_node_id_drops_parameters_and_group() -> None:
    assert base_node_id("tests/a.py::test_x[chromium]@basket") == "tests/a.py::test_x"


def test_case_refs_split_on_commas_and_spaces() -> None:
    assert parse_case_refs(" a.b, c.d  e.f ") == {"a.b", "c.d", "e.f"}


def test_worst_outcome_wins_for_a_case() -> None:
    results = RunResults(title="unit")
    results.add("case.a", "t1", PASSED)
    results.add("case.a", "t2", FAILED)
    results.add("case.a", "t3", PASSED)
    assert results.cases["case.a"].status == FAILED


def test_dry_run_writes_the_request_without_a_host(tmp_path: Path) -> None:
    results = RunResults(title="All areas")
    results.add("bvt.basket.add-product", "tests/bvt/test_basket.py::test_x", PASSED)
    output = tmp_path / "cases.json"
    DryRunReporter(output).publish(results)
    payload = json.loads(output.read_text())
    assert payload["request"]["body"]["results"][0]["case"] == "bvt.basket.add-product"
    assert "http" not in output.read_text()


def test_every_spec_file_is_in_one_area() -> None:
    spec_files = sorted(p.as_posix() for p in Path("tests").glob("[bs]*/test_*.py"))
    area_files = [f for files in AREA_SPEC_FILES.values() for f in files]
    assert sorted(area_files) == spec_files


def test_every_suite_test_has_a_case() -> None:
    spec_tests = {
        f"{path.as_posix()}::{node.name}"
        for path in Path("tests").glob("[bs]*/test_*.py")
        for node in ast.walk(ast.parse(path.read_text()))
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }
    assert spec_tests == set(CaseMap.load().cases)


def test_areas_for_cases_follow_run_order() -> None:
    refs = {"security.idor.basket-read", "bvt.account.log-out"}
    assert areas_for(refs, CaseMap.load()) == ["account", "security"]


def test_unknown_case_ref_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown"):
        areas_for({"no.such.case"}, CaseMap.load())


def test_merged_report_takes_worst_leg(tmp_path: Path) -> None:
    junit = tmp_path / "security.xml"
    junit.write_text(JUNIT)
    output = tmp_path / "report.json"
    assert case_report([str(output), str(junit), "--expect", "security"]) == 0
    results = {
        r["case"]: r["status"] for r in json.loads(output.read_text())["request"]["body"]["results"]
    }
    assert results["security.authorization.token-required"] == FAILED
    assert results["bvt.basket.add-product"] == PASSED


def test_merged_report_refuses_an_unmapped_test(tmp_path: Path) -> None:
    junit = tmp_path / "account.xml"
    junit.write_text(
        '<testsuite><testcase classname="tests.bvt.test_x" name="test_new"/></testsuite>'
    )
    output = tmp_path / "report.json"
    assert case_report([str(output), str(junit), "--expect", "account"]) == 1
    assert not output.exists()


def test_merged_report_refuses_a_missing_area(tmp_path: Path) -> None:
    junit = tmp_path / "account.xml"
    junit.write_text(JUNIT)
    output = tmp_path / "report.json"
    assert case_report([str(output), str(junit), "--expect", "account,security"]) == 1
    assert not output.exists()
