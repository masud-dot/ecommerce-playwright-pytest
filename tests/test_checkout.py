"""Checkout scenarios: form validation, price calculation, cancellation and order completion."""

import allure
import pytest
from playwright.sync_api import Page, expect

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage

pytestmark = [allure.feature("Checkout"), pytest.mark.regression]


def _start_checkout(page: Page, *product_slugs: str) -> CheckoutPage:
    inventory = InventoryPage(page)
    for slug in product_slugs or ("sauce-labs-backpack",):
        inventory.add_product_to_cart(slug)
    inventory.open_cart()
    CartPage(page).proceed_to_checkout()
    return CheckoutPage(page)


@allure.story("Customer information validation")
@pytest.mark.parametrize(
    ("first_name", "last_name", "postal_code", "expected_error"),
    [
        pytest.param("", "QA", "741101", "First Name is required", id="missing-first-name"),
        pytest.param("Suvo", "", "741101", "Last Name is required", id="missing-last-name"),
        pytest.param("Suvo", "QA", "", "Postal Code is required", id="missing-postal-code"),
    ],
)
def test_checkout_requires_customer_information(
    logged_in_page: Page, first_name: str, last_name: str, postal_code: str, expected_error: str
) -> None:
    checkout = _start_checkout(logged_in_page)
    checkout.fill_customer_information(first_name, last_name, postal_code)
    checkout.continue_to_overview()
    expect(checkout.error_message).to_contain_text(expected_error)


@allure.story("Order summary")
def test_order_summary_totals_are_consistent(logged_in_page: Page, checkout_data: dict[str, str]) -> None:
    checkout = _start_checkout(logged_in_page, "sauce-labs-backpack", "sauce-labs-bolt-t-shirt")
    checkout.fill_customer_information(**checkout_data)
    checkout.continue_to_overview()
    checkout.expect_title(CheckoutPage.OVERVIEW_TITLE)

    subtotal = checkout.subtotal_amount()
    assert subtotal == checkout.item_prices_sum(), "Subtotal should equal the sum of item prices"
    assert subtotal == pytest.approx(29.99 + 15.99)
    assert checkout.total_amount() == pytest.approx(subtotal + checkout.tax_amount(), abs=0.01)


@allure.story("Cancel checkout")
def test_cancel_checkout_returns_to_cart(logged_in_page: Page) -> None:
    checkout = _start_checkout(logged_in_page)
    checkout.cancel()
    cart = CartPage(logged_in_page)
    cart.verify_page_load()
    cart.expect_items(["Sauce Labs Backpack"])


@pytest.mark.smoke
@allure.story("Complete order")
def test_complete_checkout_end_to_end(logged_in_page: Page, checkout_data: dict[str, str]) -> None:
    checkout = _start_checkout(logged_in_page)
    checkout.fill_customer_information(**checkout_data)
    checkout.continue_to_overview()
    checkout.expect_title(CheckoutPage.OVERVIEW_TITLE)
    checkout.finish_order()
    checkout.verify_order_complete()
    checkout.expect_cart_count(0)
