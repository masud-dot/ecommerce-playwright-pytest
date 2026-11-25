"""Page object for the product inventory listing."""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Product listing: sorting, adding/removing items and opening product details."""

    PATH = "inventory.html"
    TITLE = "Products"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.product_items: Locator = page.locator('[data-test="inventory-item"]')
        self.product_names: Locator = page.locator('[data-test="inventory-item-name"]')
        self.product_prices: Locator = page.locator('[data-test="inventory-item-price"]')
        self.sort_dropdown: Locator = page.locator('[data-test="product-sort-container"]')

    def verify_page_load(self) -> None:
        self.expect_title(self.TITLE)

    def get_product_names(self) -> list[str]:
        return self.product_names.all_text_contents()

    def get_product_prices(self) -> list[float]:
        return [float(value.replace("$", "")) for value in self.product_prices.all_text_contents()]

    def sort_products(self, option: str) -> None:
        self.sort_dropdown.select_option(option)

    def add_product_to_cart(self, product_slug: str) -> None:
        self.page.locator(f'[data-test="add-to-cart-{product_slug}"]').click()

    def remove_product_from_cart(self, product_slug: str) -> None:
        self.page.locator(f'[data-test="remove-{product_slug}"]').click()

    def open_product(self, product_name: str) -> None:
        self.product_names.filter(has_text=product_name).click()
        self.page.wait_for_url("**/inventory-item.html*")
