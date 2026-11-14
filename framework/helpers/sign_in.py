"""The only way a test signs in, with one entry point per page it lands on.

An account whose session is saved has it restored into the test's own page;
otherwise it logs in through the login page under its lock, and the session is
saved when the account is reusable. Each entry point returns the landed page.
"""

from __future__ import annotations

from playwright.sync_api import Page

from framework.helpers.records import Account
from framework.helpers.session_cache import (
    account_lock,
    restore_session,
    save_session,
    saved_session,
)
from framework.pages.address_book_page import AddressBookPage
from framework.pages.basket_page import BasketPage
from framework.pages.change_password_page import ChangePasswordPage
from framework.pages.login_page import LoginPage
from framework.pages.order_history_page import OrderHistoryPage
from framework.pages.product_list_page import ProductListPage


def sign_in(page: Page, account: Account) -> None:
    """Sign the account in, from its saved session when it has one."""
    saved = saved_session(account.email) if account.reusable else None
    if saved is not None:
        restore_session(page, saved)
        return
    with account_lock(account.email):
        login = LoginPage(page)
        login.navigate()
        login.log_in(account.email, account.password)
        login.assertions.landed_on_shop()
        if account.reusable:
            save_session(page, account.email)


def sign_in_to_shop(page: Page, account: Account) -> ProductListPage:
    """Sign in and land on the product list."""
    sign_in(page, account)
    shop = ProductListPage(page)
    shop.navigate()
    return shop


def sign_in_to_basket(page: Page, account: Account) -> BasketPage:
    """Sign in and land on the basket."""
    sign_in(page, account)
    basket = BasketPage(page)
    basket.navigate()
    return basket


def sign_in_to_order_history(page: Page, account: Account) -> OrderHistoryPage:
    """Sign in and land on the order history."""
    sign_in(page, account)
    orders = OrderHistoryPage(page)
    orders.navigate()
    return orders


def sign_in_to_change_password(page: Page, account: Account) -> ChangePasswordPage:
    """Sign in and land on the change password page."""
    sign_in(page, account)
    password = ChangePasswordPage(page)
    password.navigate()
    return password


def sign_in_to_address_book(page: Page, account: Account) -> AddressBookPage:
    """Sign in and land on the address book."""
    sign_in(page, account)
    addresses = AddressBookPage(page)
    addresses.navigate()
    return addresses
