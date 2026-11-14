"""Page objects a test starts from; construction only, no navigation or sign-in."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from framework.components.navbar import Navbar
from framework.pages.basket_page import BasketPage
from framework.pages.checkout_page import CheckoutPage
from framework.pages.login_page import LoginPage
from framework.pages.product_list_page import ProductListPage
from framework.pages.registration_page import RegistrationPage


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """The login page object on the test's page."""
    return LoginPage(page)


@pytest.fixture
def registration_page(page: Page) -> RegistrationPage:
    """The registration page object on the test's page."""
    return RegistrationPage(page)


@pytest.fixture
def product_list_page(page: Page) -> ProductListPage:
    """The product list page object on the test's page."""
    return ProductListPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    """The checkout page object on the test's page."""
    return CheckoutPage(page)


@pytest.fixture
def navbar(page: Page) -> Navbar:
    """The top bar on the test's page."""
    return Navbar(page)


@pytest.fixture
def basket_page(page: Page) -> BasketPage:
    """The basket page object on the test's page."""
    return BasketPage(page)
