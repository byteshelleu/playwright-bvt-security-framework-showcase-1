"""Expected values the security assertions compare against."""

from __future__ import annotations

from pathlib import Path

SECRET_FIELDS: tuple[str, ...] = ("password", "totpSecret")
"""Fields that must never leave the server."""

NOSNIFF: str = "nosniff"
SAME_ORIGIN: str = "SAMEORIGIN"
ANY_ORIGIN: str = "*"
CONTENT_TYPE_OPTIONS: str = "X-Content-Type-Options"
FRAME_OPTIONS: str = "X-Frame-Options"
CONTENT_SECURITY_POLICY: str = "Content-Security-Policy"
ALLOW_ORIGIN: str = "Access-Control-Allow-Origin"

OK_STATUS: int = 200
TOO_MANY_REQUESTS: int = 429
SERVER_ERROR_FLOOR: int = 500

NO_TOKEN_REFUSALS: frozenset[int] = frozenset({401})
"""A request without a token is refused as unauthenticated, nothing else."""

ROLE_REFUSALS: frozenset[int] = frozenset({403})
"""A signed-in customer calling a staff endpoint is forbidden; 401 would mean the token was lost."""

LOGIN_REFUSALS: frozenset[int] = frozenset({401})
"""Wrong credentials are refused as unauthenticated."""

FOREIGN_BASKET_REFUSALS: frozenset[int] = frozenset({401, 403})
"""The shop answers 401 "Invalid BasketId" to a write into another basket; 403 is the standard."""

FOREIGN_RECORD_REFUSALS: frozenset[int] = frozenset({400, 403, 404})
"""Another customer's record: the shop answers 400 "Malicious activity detected";
403 refuses and 404 hides that it exists. A 401 or a 5xx is not a refusal."""

JWT_PAYLOAD_INDEX: int = 1
"""A JWT is header.payload.signature; the payload is the second part."""

FINDINGS_FILE: Path = Path("test-results/security/findings.json")
"""Where the failed security probes of a run are written."""

FINDING_TEXT_LIMIT: int = 2000
"""How much of a failure each finding keeps."""

SECURITY_TESTS_DIR: str = "tests/security/"
"""Node ids of security tests start with this path."""
