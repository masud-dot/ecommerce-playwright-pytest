"""Authentication scenarios: valid, invalid, locked-out and logout flows."""

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

pytestmark = [allure.feature("Authentication"), pytest.mark.regression]


@pytest.mark.smoke
@allure.story("Valid login")
def test_valid_login(page: Page, login_page: LoginPage, inventory_url: str, standard_user: dict[str, str]) -> None:
    login_page.login(standard_user["username"], standard_user["password"])
    expect(page).to_have_url(inventory_url)
    InventoryPage(page).verify_page_load()


@allure.story("Invalid login")
@pytest.mark.parametrize(
    ("username", "password", "expected_message"),
    [
        pytest.param("standard_user", "invalid_password", "Username and password do not match", id="wrong-password"),
        pytest.param("unknown_user", "secret_sauce", "Username and password do not match", id="unknown-user"),
        pytest.param("", "secret_sauce", "Username is required", id="empty-username"),
        pytest.param("standard_user", "", "Password is required", id="empty-password"),
        pytest.param("", "", "Username is required", id="empty-both"),
    ],
)
def test_invalid_login_shows_error(
    page: Page, login_page: LoginPage, app_url: str, username: str, password: str, expected_message: str
) -> None:
    login_page.login(username, password)
    expect(login_page.error_message).to_contain_text(expected_message)
    expect(page).to_have_url(app_url)


@allure.story("Locked-out user")
def test_locked_out_user_cannot_login(login_page: LoginPage, locked_user: dict[str, str]) -> None:
    login_page.login(locked_user["username"], locked_user["password"])
    expect(login_page.error_message).to_contain_text("Sorry, this user has been locked out.")


@allure.story("Access control")
def test_inventory_requires_authentication(page: Page, login_page: LoginPage, inventory_url: str) -> None:
    page.goto(inventory_url)
    expect(login_page.error_message).to_contain_text("You can only access '/inventory.html' when you are logged in")


@pytest.mark.smoke
@allure.story("Logout")
def test_logout_returns_to_login_page(logged_in_page: Page, app_url: str) -> None:
    InventoryPage(logged_in_page).logout()
    expect(logged_in_page).to_have_url(app_url)
    expect(LoginPage(logged_in_page).login_button).to_be_visible()
