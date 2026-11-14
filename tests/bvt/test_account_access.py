"""BVT: registration, login and logout."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from framework.components.navbar import Navbar
from framework.helpers.seeder import Seeder
from framework.helpers.sign_in import sign_in_to_shop
from framework.helpers.test_data import generate_account
from framework.pages.account_constants import WRONG_PASSWORD
from framework.pages.login_page import LoginPage
from framework.pages.registration_page import RegistrationPage

pytestmark = pytest.mark.bvt


def test_registration_new_customer_logs_in(
    registration_page: RegistrationPage, login_page: LoginPage, navbar: Navbar
) -> None:
    """BVT: A new customer registers and logs in with the new account.

    Steps and expected results:
    1. Open the registration page and register a new account -> the login page opens.
    2. Log in with the new account -> the product list opens.
    3. Open the account menu -> it names the new customer.
    """
    account = generate_account("signup")

    registration_page.navigate()
    registration_page.register(account)
    registration_page.assertions.registration_completed()

    login_page.log_in(account.email, account.password)
    login_page.assertions.landed_on_shop()

    navbar.open_account_menu()
    navbar.assertions.signed_in_as(account.email)


def test_login_wrong_password_refused(login_page: LoginPage, seeder: Seeder) -> None:
    """BVT: The login form refuses a wrong password.

    Steps and expected results:
    1. Open the login page and log in with a wrong password -> the form shows
       "Invalid email or password." and stays on the login page.
    """
    account = seeder.account("wrong-password")

    login_page.navigate()
    login_page.log_in(account.email, WRONG_PASSWORD)
    login_page.assertions.credentials_refused()


def test_logout_offers_login(page: Page, seeder: Seeder) -> None:
    """BVT: A signed-in customer logs out.

    Steps and expected results:
    1. Sign in and open the product list -> the products are shown.
    2. Log out from the account menu, then open the menu again -> it offers to log in.
    """
    account = seeder.account("logout")
    shop = sign_in_to_shop(page, account)

    shop.navbar.log_out()
    shop.navbar.open_account_menu()
    shop.navbar.assertions.signed_out()
