"""Unit tests for the deny-list checker, using made-up terms only."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from tools.denylist_check import compile_terms, scan

TERMS = compile_terms("# comment\n\nacme corp\nwidget.example\n")
CHECKER = Path(__file__).resolve().parents[2] / "tools" / "denylist_check.py"


def found(text: str) -> list[int]:
    return [finding.term_number for finding in scan(text, "sample", TERMS)]


def run_checker(args: list[str], stdin: str, denylist: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env={"DENYLIST": denylist, "PATH": "/usr/bin:/bin"},
        check=False,
    )


def test_comments_and_blank_lines_are_not_terms() -> None:
    assert [term.number for term in TERMS] == [3, 4]


@pytest.mark.parametrize(
    "text",
    [
        "ACME Corp",
        "acme-corp",
        "acme_corp",
        "AcmeCorp",
        "Ácmé  corp",
        "x widget.example y",
        "widget-example",
    ],
)
def test_term_variants_are_found(text: str) -> None:
    assert found(text)


@pytest.mark.parametrize("text", ["acme", "corporate acmes", "widget", "an example"])
def test_unrelated_text_is_clean(text: str) -> None:
    assert not found(text)


def test_edge_separator_is_part_of_the_term() -> None:
    edge_terms = compile_terms("abc-\n")
    assert [f.term_number for f in scan("ticket abc-42 and abc_7", "sample", edge_terms)] == [1]
    assert not list(scan("Callable xabcy abc", "sample", edge_terms))


def test_finding_names_location_and_term_number_only() -> None:
    finding = next(scan("line one\nhello AcmeCorp", "notes.md", TERMS))
    assert str(finding) == "notes.md:2: matches deny-list line 3"


def test_file_path_with_a_term_is_withheld(tmp_path: Path) -> None:
    (tmp_path / "acme_corp.md").write_text("clean\n", encoding="utf-8")
    result = run_checker(["files", str(tmp_path / "acme_corp.md")], "", "acme corp")
    assert result.returncode == 1
    assert "acme" not in result.stderr.lower()
    assert "file #1 (path withheld):1: matches deny-list line 1" in result.stderr


def test_history_findings_name_the_commit(tmp_path: Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)

    git("init", "-q")
    (tmp_path / "a.md").write_text("Acme Corp\n", encoding="utf-8")
    git("add", "a.md")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "Add a")
    result = subprocess.run(
        [sys.executable, str(CHECKER), "history", "--all"],
        capture_output=True,
        text=True,
        env={"DENYLIST": "acme corp", "PATH": "/usr/bin:/bin"},
        cwd=tmp_path,
        check=False,
    )
    assert result.returncode == 1
    assert "commit " in result.stderr
    assert "acme" not in result.stderr.lower()


def test_cli_fails_and_hides_the_term() -> None:
    result = run_checker(["text", "branch name"], "feature/acme-corp-login", "acme corp")
    assert result.returncode == 1
    assert "acme" not in result.stderr.lower()
    assert "branch name:1: matches deny-list line 1" in result.stderr


def test_cli_passes_clean_text() -> None:
    result = run_checker(["text", "branch name"], "feature/basket-tests", "acme corp")
    assert result.returncode == 0


def test_cli_fails_closed_without_a_list(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "text"],
        input="anything",
        capture_output=True,
        text=True,
        env={"PATH": "/usr/bin:/bin"},
        cwd=tmp_path,
        check=False,
    )
    assert result.returncode == 1
    assert "Failing closed" in result.stderr
