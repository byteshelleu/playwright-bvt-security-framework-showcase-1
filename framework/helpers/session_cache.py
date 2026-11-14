"""One saved signed-in session per account, so each account logs in once per run.

A session file is keyed by the account's email and holds the browser storage
(token cookie and localStorage) plus the basket id the shop keeps in
sessionStorage, which storage state does not cover. Every login and save of one
account runs under its file lock, so two sign-ins of it never overlap.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from filelock import FileLock
from playwright.sync_api import Page

from framework.constants import (
    BANNER_COOKIES,
    BANNER_DISMISSED,
    SESSION_BASKET_KEY,
    SESSION_LOCK_TIMEOUT_S,
)

SESSION_DIR = Path(tempfile.gettempdir()) / "showcase-sessions"


def session_file(email: str) -> Path:
    """Where the account's session is saved."""
    return SESSION_DIR / f"{email.lower()}.json"


def account_lock(email: str) -> FileLock:
    """The lock every login and save of the account runs under."""
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return FileLock(f"{session_file(email)}.lock", timeout=SESSION_LOCK_TIMEOUT_S)


def saved_session(email: str) -> dict[str, Any] | None:
    """The account's saved session, or None when it has not logged in yet."""
    path = session_file(email)
    if not path.is_file():
        return None
    saved: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return saved


def save_session(page: Page, email: str) -> None:
    """Save the signed-in page's storage and basket id for the account."""
    basket_id = page.evaluate(f"window.sessionStorage.getItem('{SESSION_BASKET_KEY}')")
    saved = {"state": page.context.storage_state(), "basket_id": basket_id}
    session_file(email).write_text(json.dumps(saved), encoding="utf-8")


def restore_session(page: Page, saved: dict[str, Any]) -> None:
    """Put a saved session into the page's own context before it opens the shop."""
    state = saved["state"]
    page.context.add_cookies(state["cookies"])
    entries = [item for origin in state["origins"] for item in origin["localStorage"]]
    script = "".join(
        f"window.localStorage.setItem({json.dumps(e['name'])}, {json.dumps(e['value'])});"
        for e in entries
    )
    script += f"window.sessionStorage.setItem('{SESSION_BASKET_KEY}', '{saved['basket_id']}');"
    page.context.add_init_script(script)


def banner_cookies(base_url: str) -> list[dict[str, Any]]:
    """Cookies that keep the welcome and cookie banners closed on the shop."""
    host = urlsplit(base_url).hostname or ""
    return [
        {
            "name": name,
            "value": BANNER_DISMISSED,
            "domain": host,
            "path": "/",
            "expires": -1,
            "httpOnly": False,
            "secure": False,
            "sameSite": "Lax",
        }
        for name in BANNER_COOKIES
    ]
