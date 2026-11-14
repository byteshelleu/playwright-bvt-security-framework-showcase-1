"""Strict contracts for every API answer the framework arranges data through.

A backend change then fails at the arrange step, naming the field, instead
of later in the browser.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Contract(BaseModel):
    """Unknown fields and loose types are refused."""

    model_config = ConfigDict(extra="forbid", strict=True)


class Authentication(Contract):
    """The token and basket id a login returns."""

    token: str
    bid: int
    umail: str


class LoginAnswer(Contract):
    """The answer to a login."""

    authentication: Authentication


class BasketItem(Contract):
    """A basket line as the API stores it."""

    id: int
    ProductId: int
    BasketId: str
    quantity: int
    updatedAt: str
    createdAt: str


class BasketItemAnswer(Contract):
    """The answer to adding a basket line."""

    status: str
    data: BasketItem


class AddressRecord(Contract):
    """A saved address."""

    id: int
    UserId: int
    fullName: str
    mobileNum: int
    zipCode: str
    streetAddress: str
    city: str
    state: str
    country: str
    updatedAt: str
    createdAt: str


class AddressAnswer(Contract):
    """The answer to saving an address."""

    status: str
    data: AddressRecord


class AddressListAnswer(Contract):
    """The account's saved addresses."""

    status: str
    data: list[AddressRecord]


class CardRecord(Contract):
    """A saved card as it is created."""

    id: int
    UserId: int
    fullName: str
    cardNum: int
    expMonth: int
    expYear: int
    updatedAt: str
    createdAt: str


class CardAnswer(Contract):
    """The answer to saving a card."""

    status: str
    data: CardRecord


class ListedCard(Contract):
    """A saved card as the list shows it, number masked."""

    id: int
    UserId: int
    fullName: str
    cardNum: str
    expMonth: int
    expYear: int


class CardListAnswer(Contract):
    """The account's saved cards."""

    status: str
    data: list[ListedCard]


class CheckoutAnswer(Contract):
    """The answer to placing an order."""

    orderConfirmation: str


class DeleteAnswer(Contract):
    """The answer to deleting an address or a card."""

    status: str
    data: str


class StoredBasketItem(Contract):
    """A basket line as a basket read nests it."""

    id: int
    ProductId: int
    BasketId: int
    quantity: int
    updatedAt: str
    createdAt: str


class ProductImage(Contract):
    """One alternate image of a product."""

    file: str
    format: str
    density: str


class BasketProduct(Contract):
    """A product in a basket, with its line."""

    id: int
    name: str
    description: str
    price: float | int
    deluxePrice: float | int
    image: str
    alternateImages: list[ProductImage]
    createdAt: str
    updatedAt: str
    deletedAt: str | None
    BasketItem: StoredBasketItem


class Basket(Contract):
    """A basket and its products."""

    id: int
    coupon: str | None
    UserId: int
    createdAt: str
    updatedAt: str
    Products: list[BasketProduct]


class BasketAnswer(Contract):
    """The answer to reading a basket."""

    status: str
    data: Basket
