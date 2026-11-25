"""Page object for the shopping cart."""

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class CartPage(BasePage):
    """Shopping cart: review items, remove items, continue shopping or check out."""

    TITLE = "Your Cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.items: Locator = page.locator('[data-test="inventory-item"]')
        self.item_names: Locator = page.locator('[data-test="inventory-item-name"]')
        self.checkout_button: Locator = page.get_by_role("button", name="Checkout")
        self.continue_shopping_button: Locator = page.get_by_role("button", name="Continue Shopping")

    def verify_page_load(self) -> None:
        self.expect_title(self.TITLE)

    def get_item_names(self) -> list[str]:
        return self.item_names.all_text_contents()

    def expect_items(self, names: list[str]) -> None:
        """Assert exact cart contents (in order) using Playwright's auto-retrying assertion."""
        expect(self.item_names).to_have_text(names)

    def remove_item(self, product_slug: str) -> None:
        self.page.locator(f'[data-test="remove-{product_slug}"]').click()

    def continue_shopping(self) -> None:
        self.continue_shopping_button.click()
        self.page.wait_for_url("**/inventory.html")

    def proceed_to_checkout(self) -> None:
        self.checkout_button.click()
        self.page.wait_for_url("**/checkout-step-one.html")
