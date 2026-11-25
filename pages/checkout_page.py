"""Page object for checkout information, overview and completion steps."""

import re

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage

_AMOUNT = re.compile(r"\$(\d+(?:\.\d{2})?)")


def _parse_amount(label: str) -> float:
    match = _AMOUNT.search(label)
    if match is None:
        raise ValueError(f"No dollar amount found in label: {label!r}")
    return float(match.group(1))


class CheckoutPage(BasePage):
    """Checkout flow: customer information, order overview and confirmation."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.first_name: Locator = page.get_by_placeholder("First Name")
        self.last_name: Locator = page.get_by_placeholder("Last Name")
        self.postal_code: Locator = page.get_by_placeholder("Zip/Postal Code")
        self.continue_button: Locator = page.get_by_role("button", name="Continue")
        self.finish_button: Locator = page.get_by_role("button", name="Finish")
        self.cancel_button: Locator = page.get_by_role("button", name="Cancel")
        self.error_message: Locator = page.locator('[data-test="error"]')
        self.item_prices: Locator = page.locator('[data-test="inventory-item-price"]')
        self.subtotal: Locator = page.locator('[data-test="subtotal-label"]')
        self.tax: Locator = page.locator('[data-test="tax-label"]')
        self.total: Locator = page.locator('[data-test="total-label"]')
        self.complete_header: Locator = page.locator('[data-test="complete-header"]')

    INFORMATION_TITLE = "Checkout: Your Information"
    OVERVIEW_TITLE = "Checkout: Overview"

    def fill_customer_information(self, first_name: str, last_name: str, postal_code: str) -> None:
        self.expect_title(self.INFORMATION_TITLE)
        for field, value in (
            (self.first_name, first_name),
            (self.last_name, last_name),
            (self.postal_code, postal_code),
        ):
            self._fill_and_confirm(field, value)

    @staticmethod
    def _fill_and_confirm(field: Locator, value: str, attempts: int = 3) -> None:
        """Fill a React-controlled input and confirm the value stuck.

        The form can re-render immediately after the route mounts, which may wipe a value
        typed too early. Re-filling until the value is confirmed removes that race.
        """
        for _ in range(attempts):
            field.fill(value)
            if field.input_value() == value:
                break
        expect(field).to_have_value(value)

    def continue_to_overview(self) -> None:
        self.continue_button.click()

    def cancel(self) -> None:
        self.cancel_button.click()

    def finish_order(self) -> None:
        self.finish_button.click()
        self.page.wait_for_url("**/checkout-complete.html")

    def item_prices_sum(self) -> float:
        return round(sum(_parse_amount(p) for p in self.item_prices.all_text_contents()), 2)

    def subtotal_amount(self) -> float:
        return _parse_amount(self.subtotal.inner_text())

    def tax_amount(self) -> float:
        return _parse_amount(self.tax.inner_text())

    def total_amount(self) -> float:
        return _parse_amount(self.total.inner_text())

    def verify_order_complete(self) -> None:
        expect(self.complete_header).to_have_text("Thank you for your order!")
