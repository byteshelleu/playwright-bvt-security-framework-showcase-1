"""The shop's REST API: the channel the seeder and the fixtures create data through.

Every call is one request whose answer is checked against its contract.
A spec never imports this module; it seeds through the `seeder` fixture.
"""

from __future__ import annotations

from playwright.sync_api import APIRequestContext, APIResponse
from pydantic import BaseModel

from framework.api_constants import (
    ADDRESS_TEMPLATE,
    ADDRESSES,
    BASKET_ITEM_TEMPLATE,
    BASKET_ITEMS,
    BASKET_TEMPLATE,
    CARD_TEMPLATE,
    CARDS,
    CHECKOUT_TEMPLATE,
    LOGIN,
    SECURITY_QUESTION_ID,
    USERS,
)
from framework.helpers.api_contracts import (
    AddressAnswer,
    AddressListAnswer,
    AddressRecord,
    BasketAnswer,
    BasketItemAnswer,
    CardAnswer,
    CardListAnswer,
    CheckoutAnswer,
    DeleteAnswer,
    ListedCard,
    LoginAnswer,
)
from framework.helpers.records import Account, Address, ApiSession, Card, DeliveryMethod, Product


class ApiError(RuntimeError):
    """An arrange request the shop refused."""


def _parsed[ContractT: BaseModel](
    response: APIResponse, contract: type[ContractT], action: str
) -> ContractT:
    if not response.ok:
        raise ApiError(f"{action}: HTTP {response.status} {response.text()[:200]}")
    return contract.model_validate(response.json())


class ApiClient:
    """One method per arrange request."""

    def __init__(self, request: APIRequestContext) -> None:
        """Keep the request context bound to the shop's base URL."""
        self.request = request

    def register(self, account: Account) -> None:
        """Create the account."""
        response = self.request.post(
            USERS,
            data={
                "email": account.email,
                "password": account.password,
                "passwordRepeat": account.password,
                "securityQuestion": {"id": SECURITY_QUESTION_ID},
                "securityAnswer": account.security_answer,
            },
        )
        if not response.ok:
            raise ApiError(f"register {account.label}: HTTP {response.status}")

    def login(self, account: Account) -> ApiSession:
        """Log the account in and return its token and basket."""
        answer = _parsed(
            self.request.post(LOGIN, data={"email": account.email, "password": account.password}),
            LoginAnswer,
            f"login {account.label}",
        )
        auth = answer.authentication
        return ApiSession(account=account, token=auth.token, basket_id=auth.bid)

    def add_to_basket(self, session: ApiSession, product: Product) -> int:
        """Add one of the product to the account's basket."""
        data = {"ProductId": product.id, "BasketId": str(session.basket_id), "quantity": 1}
        response = self.request.post(BASKET_ITEMS, data=data, headers=session.headers)
        return _parsed(response, BasketItemAnswer, f"add {product.name}").data.id

    def basket_item_ids(self, session: ApiSession) -> list[int]:
        """The ids of the lines in the account's basket."""
        response = self.request.get(
            BASKET_TEMPLATE.format(basket_id=session.basket_id), headers=session.headers
        )
        products = _parsed(response, BasketAnswer, "read basket").data.Products
        return [product.BasketItem.id for product in products]

    def remove_basket_item(self, session: ApiSession, item_id: int) -> None:
        """Delete one basket line."""
        response = self.request.delete(
            BASKET_ITEM_TEMPLATE.format(item_id=item_id), headers=session.headers
        )
        if not response.ok:
            raise ApiError(f"remove basket item {item_id}: HTTP {response.status}")

    def add_address(self, session: ApiSession, address: Address) -> int:
        """Save an address and return its id."""
        data = {
            "fullName": address.full_name,
            "mobileNum": address.mobile,
            "zipCode": address.zip_code,
            "streetAddress": address.street,
            "city": address.city,
            "state": address.state,
            "country": address.country,
        }
        response = self.request.post(ADDRESSES, data=data, headers=session.headers)
        return _parsed(response, AddressAnswer, "add address").data.id

    def addresses(self, session: ApiSession) -> list[AddressRecord]:
        """The account's saved addresses."""
        response = self.request.get(ADDRESSES, headers=session.headers)
        return _parsed(response, AddressListAnswer, "list addresses").data

    def remove_address(self, session: ApiSession, address_id: int) -> None:
        """Delete one saved address."""
        response = self.request.delete(
            ADDRESS_TEMPLATE.format(address_id=address_id), headers=session.headers
        )
        _parsed(response, DeleteAnswer, f"remove address {address_id}")

    def add_card(self, session: ApiSession, card: Card) -> int:
        """Save a card and return its id."""
        data = {
            "fullName": card.full_name,
            "cardNum": card.number,
            "expMonth": card.exp_month,
            "expYear": card.exp_year,
        }
        response = self.request.post(CARDS, data=data, headers=session.headers)
        return _parsed(response, CardAnswer, "add card").data.id

    def cards(self, session: ApiSession) -> list[ListedCard]:
        """The account's saved cards."""
        response = self.request.get(CARDS, headers=session.headers)
        return _parsed(response, CardListAnswer, "list cards").data

    def remove_card(self, session: ApiSession, card_id: int) -> None:
        """Delete one saved card."""
        response = self.request.delete(
            CARD_TEMPLATE.format(card_id=card_id), headers=session.headers
        )
        _parsed(response, DeleteAnswer, f"remove card {card_id}")

    def checkout(
        self, session: ApiSession, address_id: int, card_id: int, delivery: DeliveryMethod
    ) -> str:
        """Place the basket as an order and return its id."""
        details = {
            "paymentId": str(card_id),
            "addressId": str(address_id),
            "deliveryMethodId": str(delivery.id),
        }
        response = self.request.post(
            CHECKOUT_TEMPLATE.format(basket_id=session.basket_id),
            data={"orderDetails": details},
            headers=session.headers,
        )
        return _parsed(response, CheckoutAnswer, "checkout").orderConfirmation
