"""BVT: account settings, the password and the address book."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from framework.components.navbar import Navbar
from framework.helpers.seeder import Seeder
from framework.helpers.sign_in import sign_in_to_address_book, sign_in_to_change_password
from framework.helpers.test_data import generate_address, new_password
from framework.pages.login_page import LoginPage

pytestmark = pytest.mark.bvt


def test_change_password_then_log_in(
    page: Page, seeder: Seeder, navbar: Navbar, login_page: LoginPage
) -> None:
    """BVT: A customer changes the password and logs in with the new one.

    Steps and expected results:
    1. Sign in and open Change Password -> the form is shown.
    2. Change the password -> "Your password was successfully changed." is shown.
    3. Log out and log in with the new password -> the product list opens.
    """
    account = seeder.account("password")
    password = new_password()
    password_page = sign_in_to_change_password(page, account)

    password_page.change(account.password, password)
    password_page.assertions.password_changed()

    navbar.log_out()
    login_page.navigate()
    login_page.log_in(account.email, password)
    login_page.assertions.landed_on_shop()


def test_address_book_saves_address(page: Page, seeder: Seeder) -> None:
    """BVT: A customer saves a new address in the address book.

    Steps and expected results:
    1. Sign in and open the address book -> it is shown.
    2. Add a new address -> it is listed under its owner's name.
    """
    account = seeder.account("address")
    address = generate_address()
    address_book = sign_in_to_address_book(page, account)

    address_book.add(address)
    address_book.assertions.lists(address)
