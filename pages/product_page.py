"""Page object for an individual product details page."""

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class ProductPage(BasePage):
    """Product details: name, description, price and navigation back to the listing."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # Scoped to the details-only container: the listing reuses the same data-test ids.
        details = page.locator(".inventory_details_container")
        self.name: Locator = details.locator('[data-test="inventory-item-name"]')
        self.description: Locator = details.locator('[data-test="inventory-item-desc"]')
        self.price: Locator = details.locator('[data-test="inventory-item-price"]')
        self.back_button: Locator = page.get_by_role("button", name="Back to products")

    def verify_product(self, name: str, price: str) -> None:
        expect(self.name).to_have_text(name)
        expect(self.price).to_have_text(price)
        expect(self.description).not_to_be_empty()

    def back_to_products(self) -> None:
        self.back_button.click()
        self.page.wait_for_url("**/inventory.html")
