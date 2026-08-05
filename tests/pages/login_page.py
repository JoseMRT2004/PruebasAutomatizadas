"""Page object for the login flow."""

from tests.pages.base_page import BasePage


class LoginPage(BasePage):
    """Wraps the login form at ``/login``."""

    def open(self):
        return super().open("/login")

    def login(self, username, password):
        """Fill the credentials and click the submit button."""
        self.fill("#username", username)
        self.fill("#password", password)
        self.click_submit()
        return self

    @property
    def error_message(self):
        return self.element_text("#form-error")

    def is_on_login(self):
        return self.current_url.rstrip("/").endswith("/login")
