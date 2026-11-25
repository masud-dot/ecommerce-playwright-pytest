"""Shared fixtures, command-line options and reporting hooks for UI and API tests."""

import contextlib
from collections.abc import Generator
from urllib.parse import urljoin

import allure
import pytest
from playwright.sync_api import APIRequestContext, Page, Playwright, expect

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.config_loader import get_checkout_data, get_environment, get_user


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--env",
        action="store",
        default="qa",
        help="Environment key from config/environments.json (default: qa)",
    )


# --------------------------------------------------------------------------- #
# Configuration and test-data fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def environment(pytestconfig: pytest.Config) -> dict[str, str]:
    return get_environment(pytestconfig.getoption("--env"))


@pytest.fixture(scope="session")
def app_url(environment: dict[str, str]) -> str:
    return environment["base_url"]


@pytest.fixture(scope="session")
def inventory_url(app_url: str) -> str:
    return urljoin(app_url, InventoryPage.PATH)


@pytest.fixture(scope="session")
def standard_user() -> dict[str, str]:
    return get_user("standard_user")


@pytest.fixture(scope="session")
def locked_user() -> dict[str, str]:
    return get_user("locked_out_user")


@pytest.fixture(scope="session")
def checkout_data() -> dict[str, str]:
    return get_checkout_data()


# --------------------------------------------------------------------------- #
# Browser fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture
def login_page(page: Page, app_url: str) -> LoginPage:
    """Open the login screen with clean client-side storage."""
    login = LoginPage(page)
    login.navigate(app_url)
    # SauceDemo keeps the cart in localStorage; start every test from a known-empty state.
    page.evaluate("() => { window.localStorage.clear(); window.sessionStorage.clear(); }")
    return login


@pytest.fixture
def logged_in_page(login_page: LoginPage, inventory_url: str, standard_user: dict[str, str]) -> Page:
    """Return a page logged in as the standard user, failing fast if login did not work."""
    with allure.step("Log in as standard user"):
        login_page.login(standard_user["username"], standard_user["password"])
        expect(login_page.page).to_have_url(inventory_url)
    InventoryPage(login_page.page).expect_cart_count(0)
    return login_page.page


# --------------------------------------------------------------------------- #
# API fixtures
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def api_context(playwright: Playwright, environment: dict[str, str]) -> Generator[APIRequestContext, None, None]:
    """A session-scoped API client, independent from browser cookies."""
    request_context = playwright.request.new_context(
        base_url=environment["api_base_url"],
        extra_http_headers={"Accept": "application/json"},
        timeout=15_000,
    )
    yield request_context
    request_context.dispose()


# --------------------------------------------------------------------------- #
# Reporting: attach a screenshot to Allure when a UI test fails
# --------------------------------------------------------------------------- #
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = getattr(item, "funcargs", {}).get("page")
        if page is not None and not page.is_closed():
            with contextlib.suppress(Exception):
                allure.attach(
                    page.screenshot(full_page=True),
                    name="failure-screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
