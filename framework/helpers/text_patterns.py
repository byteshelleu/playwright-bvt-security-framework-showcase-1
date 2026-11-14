"""The patterns a locator matches a text with, one definition per shape."""

from __future__ import annotations

import re


def exact_text(text: str) -> re.Pattern[str]:
    """The whole text and nothing else, trimmed."""
    return re.compile(rf"^\s*{re.escape(text)}\s*$")


def ends_with_number(number: int) -> re.Pattern[str]:
    """A text whose last word is exactly this number, so 1 never matches 11."""
    return re.compile(rf"(^|\D){number}\s*$")


def starts_with_text(text: str) -> re.Pattern[str]:
    """A text that opens with these words."""
    return re.compile(rf"^\s*{re.escape(text)}")
