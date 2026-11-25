"""Shared behaviour for every authenticated SauceDemo page (header, cart badge, side menu)."""

from playwright.sync_api import Locator, Page, expect


class BasePage:
    """Base page object exposing the application header available after login."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.title: Locator = page.locator('[data-test="title"]')
        self.cart_link: Locator = page.locator('[data-test="shopping-cart-link"]')
        self.cart_badge: Locator = page.locator('[data-test="shopping-cart-badge"]')
        self.menu_button: Locator = page.get_by_role("button", name="Open Menu")
        self.menu_panel: Locator = page.locator(".bm-menu-wrap")
        self.logout_link: Locator = page.locator('[data-test="logout-sidebar-link"]')

    def expect_title(self, text: str) -> None:
        expect(self.title).to_have_text(text)

    def expect_cart_count(self, count: int) -> None:
        """Assert the cart badge value; an empty cart renders no badge at all."""
        if count == 0:
            expect(self.cart_badge).to_have_count(0)
        else:
            expect(self.cart_badge).to_have_text(str(count))

    def open_cart(self) -> None:
        self.cart_link.click()
        self.page.wait_for_url("**/cart.html")

    def logout(self) -> None:
        self.menu_button.click()
        # The side menu slides in with a CSS transition; wait until it is fully open.
        expect(self.menu_panel).to_have_attribute("aria-hidden", "false")
        expect(self.logout_link).to_be_visible()
        self.logout_link.click()
