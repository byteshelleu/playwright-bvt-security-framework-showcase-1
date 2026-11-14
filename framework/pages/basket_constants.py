"""Names, test ids and icons of the basket page."""

from __future__ import annotations

CHECKOUT_NAME: str = "Checkout"
TOTAL_TEST_ID: str = "price"
TOTAL_TEMPLATE: str = "Total Price: {price}"
INCREASE_ICON: str = "plus-square"
DECREASE_ICON: str = "minus-square"
REMOVE_ICON: str = "trash-alt"
LINE_TEMPLATE: str = "{quantity} {price}"
"""A basket line shows the quantity, then the unit price."""
RAISED_QUANTITY: int = 2
"""The quantity after one increase from a single item."""
