"""Probes of more than one request, request bodies, and reading what an attacker would."""

from __future__ import annotations

import base64
import json
from typing import Any

from framework.api_constants import USER_TEMPLATE
from framework.helpers.records import ApiSession, Product
from framework.security.client import SecurityClient
from framework.security.payloads import WRONG_PASSWORD_TEMPLATE
from framework.security.security_constants import JWT_PAYLOAD_INDEX

BASE64_BLOCK = 4


def jwt_claims(token: str) -> dict[str, Any]:
    """The token's payload, decoded without verifying it, as anyone holding it can."""
    payload = token.split(".")[JWT_PAYLOAD_INDEX]
    padded = payload + "=" * (-len(payload) % BASE64_BLOCK)
    claims: dict[str, Any] = json.loads(base64.urlsafe_b64decode(padded))
    return claims


def own_user_route(session: ApiSession) -> str:
    """The route of the session's own user record, by the id its token carries."""
    return USER_TEMPLATE.format(user_id=jwt_claims(session.token)["data"]["id"])


def basket_item(product: Product, basket_id: int) -> dict[str, Any]:
    """A request body putting one of the product into a basket."""
    return {"ProductId": product.id, "BasketId": str(basket_id), "quantity": 1}


def search_query(term: str) -> dict[str, str]:
    """The query string of a product search."""
    return {"q": term}


def unchanged_password(password: str) -> dict[str, str]:
    """A password change that keeps the same password."""
    return {"current": password, "new": password, "repeat": password}


def failed_login_statuses(client: SecurityClient, email: str, attempts: int) -> list[int]:
    """The status of each login in a burst with wrong passwords."""
    return [
        client.login(email, WRONG_PASSWORD_TEMPLATE.format(attempt=n)).status
        for n in range(attempts)
    ]
