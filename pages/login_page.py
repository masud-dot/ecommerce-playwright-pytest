"""Page object for the SauceDemo login screen."""

from playwright.sync_api import Locator, Page


class LoginPage:
    """Page object for SauceDemo authentication."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.username_input: Locator = page.get_by_placeholder("Username")
        self.password_input: Locator = page.get_by_placeholder("Password")
        self.login_button: Locator = page.get_by_role("button", name="Login")
        self.error_message: Locator = page.locator('[data-test="error"]')

    def navigate(self, base_url: str) -> None:
        self.page.goto(base_url)

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
