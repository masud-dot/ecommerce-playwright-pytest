"""Page Object Model classes for the SauceDemo application."""

from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from pages.product_page import ProductPage

__all__ = ["BasePage", "CartPage", "CheckoutPage", "InventoryPage", "LoginPage", "ProductPage"]
