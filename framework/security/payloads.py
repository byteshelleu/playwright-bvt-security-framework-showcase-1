"""Probe payloads: data only, and never destructive."""

from __future__ import annotations

from framework.constants import EMAIL_DOMAIN

SQL_TAUTOLOGY: str = "' OR 1=1--"
"""Makes a WHERE clause always true if the input reaches SQL unescaped."""

SQL_BREAKOUT: str = "'))"
"""Closes the search query's parentheses early; an unescaped input breaks the SQL."""

LONE_QUOTE: str = "'"
"""The smallest input that breaks unescaped SQL."""

SEARCH_PROBES: tuple[str, ...] = (LONE_QUOTE, SQL_BREAKOUT)
SEARCH_PROBE_IDS: tuple[str, ...] = ("lone-quote", "breakout")

UNKNOWN_EMAIL: str = f"nobody@{EMAIL_DOMAIN}"
PLAIN_SEARCH_TERM: str = "apple"
WRONG_PASSWORD_TEMPLATE: str = "wrong-{attempt}"
LOGIN_BURST_ATTEMPTS: int = 30
"""Failed logins in a row after which a protected login must start answering 429."""
