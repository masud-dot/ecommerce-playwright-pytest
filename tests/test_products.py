"""Product catalogue scenarios: listing, sorting and product details."""

import allure
import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
from pages.product_page import ProductPage

pytestmark = [allure.feature("Product catalogue"), pytest.mark.regression]

EXPECTED_PRODUCT_COUNT = 6


@pytest.mark.smoke
@allure.story("Inventory listing")
def test_product_inventory_loads(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.verify_page_load()
    names = inventory.get_product_names()
    prices = inventory.get_product_prices()
    assert len(names) == EXPECTED_PRODUCT_COUNT, f"Expected {EXPECTED_PRODUCT_COUNT} products, found {len(names)}"
    assert len(set(names)) == len(names), "Product names should be unique"
    assert len(prices) == len(names)
    assert all(price > 0 for price in prices)


@allure.story("Sorting")
@pytest.mark.parametrize(
    ("sort_option", "sort_key", "reverse"),
    [
        pytest.param("az", "name", False, id="name-a-to-z"),
        pytest.param("za", "name", True, id="name-z-to-a"),
        pytest.param("lohi", "price", False, id="price-low-to-high"),
        pytest.param("hilo", "price", True, id="price-high-to-low"),
    ],
)
def test_product_sorting(logged_in_page: Page, sort_option: str, sort_key: str, reverse: bool) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.sort_products(sort_option)
    if sort_key == "name":
        actual: list[str] | list[float] = inventory.get_product_names()
        expected = sorted(actual, key=str.casefold, reverse=reverse)
    else:
        actual = inventory.get_product_prices()
        expected = sorted(actual, reverse=reverse)
    assert actual == expected, f"Sort option '{sort_option}' did not produce the expected order"


@allure.story("Product details")
def test_product_details_and_back_navigation(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.open_product("Sauce Labs Backpack")
    product = ProductPage(logged_in_page)
    product.verify_product("Sauce Labs Backpack", "$29.99")
    product.back_to_products()
    inventory.verify_page_load()
