"""Typed records passed between the seeder, the API client and the tests."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Account:
    """A shop account; secrets stay out of reprs and reports."""

    label: str
    email: str
    password: str = field(repr=False)
    security_answer: str = field(repr=False)
    reusable: bool = False
    """Whether its signed-in session is saved and reused; generated per-test accounts are not."""


@dataclass(frozen=True)
class ApiSession:
    """A signed-in account as the API sees it."""

    account: Account
    token: str = field(repr=False)
    basket_id: int

    @property
    def headers(self) -> dict[str, str]:
        """The bearer header for this session."""
        return {"Authorization": f"Bearer {self.token}"}


@dataclass(frozen=True)
class Product:
    """A catalogue product."""

    id: int
    name: str
    price: float


@dataclass(frozen=True)
class DeliveryMethod:
    """A delivery speed offered at checkout."""

    id: int
    name: str
    price: float


@dataclass(frozen=True)
class Address:
    """A delivery address; `id` is set once it is saved."""

    full_name: str
    mobile: int
    zip_code: str
    street: str
    city: str
    state: str
    country: str
    id: int | None = None


@dataclass(frozen=True)
class Card:
    """A payment card; `id` is set once it is saved."""

    full_name: str
    number: int = field(repr=False)
    exp_month: int
    exp_year: int
    id: int | None = None

    @property
    def last_four(self) -> str:
        """The digits the shop shows unmasked."""
        return str(self.number)[-4:]


@dataclass(frozen=True)
class SeededBasket:
    """Basket lines the seeder created."""

    item_ids: tuple[int, ...]


@dataclass(frozen=True)
class SeededOrder:
    """An order placed by the seeder."""

    order_id: str
    total: float
