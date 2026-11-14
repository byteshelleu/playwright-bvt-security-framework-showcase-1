"""The shop's API routes, spelled once for the API client and the security suite."""

from __future__ import annotations

HOME: str = "/"
APPLICATION_VERSION: str = "/rest/admin/application-version"
LOGIN: str = "/rest/user/login"
WHOAMI: str = "/rest/user/whoami"
CHANGE_PASSWORD: str = "/rest/user/change-password"
AUTHENTICATION_DETAILS: str = "/rest/user/authentication-details"
USERS: str = "/api/Users"
USER_TEMPLATE: str = "/api/Users/{user_id}"
SEARCH: str = "/rest/products/search"
BASKET_ITEMS: str = "/api/BasketItems"
BASKET_ITEM_TEMPLATE: str = "/api/BasketItems/{item_id}"
BASKET_TEMPLATE: str = "/rest/basket/{basket_id}"
CHECKOUT_TEMPLATE: str = "/rest/basket/{basket_id}/checkout"
ADDRESSES: str = "/api/Addresss"
ADDRESS_TEMPLATE: str = "/api/Addresss/{address_id}"
CARDS: str = "/api/Cards"
CARD_TEMPLATE: str = "/api/Cards/{card_id}"
ORDER_HISTORY: str = "/rest/order-history"
ALL_ORDERS: str = "/rest/order-history/orders"

SECURITY_QUESTION_ID: int = 1
"""The question every generated account answers at sign-up."""

CUSTOMER_DATA_ROUTES: tuple[str, ...] = (USERS, CARDS, ADDRESSES, BASKET_TEMPLATE, ORDER_HISTORY)
"""Routes holding a customer's data; a template is filled with the customer's own basket."""
