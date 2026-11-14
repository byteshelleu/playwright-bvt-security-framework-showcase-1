"""The CI areas and the spec files each one runs, in run order."""

from __future__ import annotations

CI_AREAS: tuple[str, ...] = ("account", "shopping", "security")
"""One CI job per area, run one after another in this order."""

AREA_SPEC_FILES: dict[str, tuple[str, ...]] = {
    "account": (
        "tests/bvt/test_account_access.py",
        "tests/bvt/test_account_settings.py",
    ),
    "shopping": (
        "tests/bvt/test_product_search.py",
        "tests/bvt/test_basket.py",
        "tests/bvt/test_checkout.py",
        "tests/bvt/test_order_history.py",
    ),
    "security": (
        "tests/security/test_access_control.py",
        "tests/security/test_authorization.py",
        "tests/security/test_rate_limiting.py",
        "tests/security/test_security_headers.py",
        "tests/security/test_sensitive_data.py",
        "tests/security/test_injection.py",
    ),
}
"""Every spec file belongs to exactly one area."""

XDIST_GROUP_BASKET: str = "basket"
"""The basket cases share the shopper account, so they run on one worker, never at once."""
