"""How the shop writes values on screen."""

from __future__ import annotations

from framework.constants import CURRENCY_SYMBOL, PRICE_DECIMALS


def price_text(amount: float) -> str:
    """A price as the shop shows it, e.g. 1.99¤."""
    return f"{amount:.{PRICE_DECIMALS}f}{CURRENCY_SYMBOL}"
