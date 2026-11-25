"""Shopping cart scenarios: add, remove, multiple items and navigation."""

import allure
import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

pytestmark = [allure.feature("Shopping cart"), pytest.mark.regression]


@pytest.mark.smoke
@allure.story("Add to cart")
def test_add_product_to_cart(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.add_product_to_cart("sauce-labs-backpack")
    inventory.expect_cart_count(1)
    inventory.open_cart()
    cart = CartPage(logged_in_page)
    cart.verify_page_load()
    cart.expect_items(["Sauce Labs Backpack"])


@allure.story("Remove from cart")
def test_remove_product_from_cart_page(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.add_product_to_cart("sauce-labs-backpack")
    inventory.open_cart()
    cart = CartPage(logged_in_page)
    cart.remove_item("sauce-labs-backpack")
    cart.expect_items([])
    cart.expect_cart_count(0)


@allure.story("Remove from cart")
def test_remove_product_from_inventory_page(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.add_product_to_cart("sauce-labs-onesie")
    inventory.expect_cart_count(1)
    inventory.remove_product_from_cart("sauce-labs-onesie")
    inventory.expect_cart_count(0)


@allure.story("Add to cart")
def test_add_multiple_products_to_cart(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.add_product_to_cart("sauce-labs-backpack")
    inventory.add_product_to_cart("sauce-labs-bike-light")
    inventory.expect_cart_count(2)
    inventory.open_cart()
    cart = CartPage(logged_in_page)
    cart.expect_items(["Sauce Labs Backpack", "Sauce Labs Bike Light"])


@allure.story("Cart persistence")
def test_cart_persists_after_continue_shopping(logged_in_page: Page) -> None:
    inventory = InventoryPage(logged_in_page)
    inventory.add_product_to_cart("sauce-labs-fleece-jacket")
    inventory.open_cart()
    cart = CartPage(logged_in_page)
    cart.continue_shopping()
    inventory.verify_page_load()
    inventory.expect_cart_count(1)
