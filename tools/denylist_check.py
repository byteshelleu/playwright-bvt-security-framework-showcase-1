"""Fail when any deny-listed term appears in the repository or its metadata.

The deny-list is read from the DENYLIST environment variable (CI, from a
repository secret) or from .claude/private/denylist.txt (local, gitignored).
One term per line; blank lines and lines starting with '#' are ignored.

Matching ignores case, accents and the separators between words, so the term
"acme corp" also matches "ACME-Corp", "acme_corp" and "AcmeCorp".

Findings name the location and the term's line number in the deny-list, never
the term itself, so CI logs do not leak what the list contains.

Usage:
    denylist_check.py files [PATH ...]   file paths and contents (default: all tracked files)
    denylist_check.py message FILE       a commit message file (commit-msg hook)
    denylist_check.py text LABEL         text read from stdin, e.g. a branch name or PR body
    denylist_check.py history [RANGE]    every commit's author, message and diff (default: HEAD)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

LOCAL_LIST = Path(".claude/private/denylist.txt")
ENV_VAR = "DENYLIST"
SEPARATORS = r"[\s_\-.]*"


@dataclass(frozen=True)
class Term:
    number: int
    pattern: re.Pattern[str]


@dataclass(frozen=True)
class Finding:
    location: str
    term_number: int

    def __str__(self) -> str:
        return f"{self.location}: matches deny-list line {self.term_number}"


def normalise(text: str) -> str:
    """Lower-case the text and strip accents, so matching ignores both."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold()


def compile_terms(raw: str) -> list[Term]:
    """One pattern per deny-list line; comments and blank lines are skipped."""
    terms = []
    for number, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pattern = term_pattern(normalise(stripped))
        if pattern is not None:
            terms.append(Term(number, pattern))
    return terms


def term_pattern(normalised: str) -> re.Pattern[str] | None:
    """The pattern for one term; a separator at either end of it is kept.

    "abc-" must not match inside "xabcy", so an edge separator stays required.
    """
    words = [w for w in re.split(r"[\s_\-.]+", normalised) if w]
    if not words:
        return None
    lead = r"[\s_\-.]+" if re.match(r"[\s_\-.]", normalised) else ""
    trail = r"[\s_\-.]+" if re.search(r"[\s_\-.]$", normalised) else ""
    return re.compile(lead + SEPARATORS.join(re.escape(w) for w in words) + trail)


def load_terms() -> list[Term]:
    """The deny-list from DENYLIST, else the local file; fail closed when neither exists."""
    raw = os.environ.get(ENV_VAR, "")
    if not raw.strip() and LOCAL_LIST.is_file():
        raw = LOCAL_LIST.read_text(encoding="utf-8")
    terms = compile_terms(raw)
    if not terms:
        sys.exit(f"No deny-list found: set {ENV_VAR} or create {LOCAL_LIST}. Failing closed.")
    return terms


def scan(text: str, location: str, terms: Iterable[Term]) -> Iterator[Finding]:
    """Every line of the text that matches a term."""
    lines = enumerate(normalise(text).splitlines(), start=1)
    return (
        Finding(f"{location}:{number}", term.number)
        for number, line in lines
        for term in terms
        if term.pattern.search(line)
    )


def git(*args: str) -> str:
    """Run a git command and return its output."""
    return subprocess.run(
        ["git", *args], check=True, capture_output=True, text=True, errors="replace"
    ).stdout


def scan_files(paths: list[str], terms: list[Term]) -> Iterator[Finding]:
    """Scan paths and contents; a path that holds a term is withheld from the report."""
    for index, path in enumerate(paths or git("ls-files").splitlines(), start=1):
        path_findings = list(scan(path, f"file #{index} (path withheld)", terms))
        yield from path_findings
        label = f"file #{index} (path withheld)" if path_findings else path
        file = Path(path)
        if file.is_file():
            yield from scan(file.read_text(encoding="utf-8", errors="replace"), label, terms)


def scan_history(revision_range: str, terms: list[Term]) -> Iterator[Finding]:
    """Scan every commit's author, message and diff in the range, by commit."""
    marker = "\x1ecommit "
    log = git("log", "--patch", f"--format={marker}%H%n%an <%ae>%n%cn <%ce>%n%B", revision_range)
    for chunk in log.split(marker)[1:]:
        sha, _, body = chunk.partition("\n")
        yield from scan(body, f"commit {sha[:12]}", terms)


def findings_for(mode: str, args: list[str], terms: list[Term]) -> list[Finding]:
    """Run the scan one mode asks for."""
    if mode == "files":
        return list(scan_files(args, terms))
    if mode == "message":
        return list(scan(Path(args[0]).read_text(encoding="utf-8"), "commit message", terms))
    if mode == "text":
        return list(scan(sys.stdin.read(), args[0] if args else "stdin", terms))
    return list(scan_history(args[0] if args else "HEAD", terms))


def main(argv: list[str]) -> int:
    """Print the findings; exit 1 when there are any."""
    if not argv or argv[0] not in {"files", "message", "text", "history"}:
        sys.stderr.write(f"{__doc__}\n")
        return 2
    findings = findings_for(argv[0], argv[1:], load_terms())
    sys.stderr.writelines(f"{finding}\n" for finding in findings)
    if findings:
        sys.stderr.write(f"Deny-list check failed: {len(findings)} finding(s).\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
