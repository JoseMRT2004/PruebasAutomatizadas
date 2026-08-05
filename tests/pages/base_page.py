"""Base page object with shared Selenium helpers for the Page Object Model."""

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    """Common helpers shared by every page object.

    All page objects navigate relative to ``base_url`` and expose small,
    readable methods so tests stay declarative.
    """

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def open(self, path):
        """Navigate the browser to ``base_url + path``."""
        self.driver.get(f"{self.base_url}{path}")
        return self

    @property
    def current_url(self):
        return self.driver.current_url

    @property
    def body_text(self):
        return self.driver.find_element(By.TAG_NAME, "body").text

    def find(self, by=By.CSS_SELECTOR, value="", timeout=10):
        """Wait until an element matching ``by``/``value`` is present, then return it."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def find_all(self, by=By.CSS_SELECTOR, value=""):
        return self.driver.find_elements(by, value)

    def wait_for_element(self, selector, timeout=10):
        return self.find(By.CSS_SELECTOR, selector, timeout)

    def wait_for_url_contains(self, text, timeout=10):
        WebDriverWait(self.driver, timeout).until(lambda d: text in d.current_url)

    def wait_for_url_ends_with(self, suffix, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.current_url.rstrip("/").endswith(suffix)
        )

    def wait_for_text(self, selector, text, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, selector), text)
        )

    def fill(self, selector, value):
        """Clear and type ``value`` into the element matching ``selector``."""
        element = self.find(By.CSS_SELECTOR, selector)
        element.clear()
        if value is not None:
            element.send_keys(str(value))
        return element

    def click(self, selector):
        element = self.find(By.CSS_SELECTOR, selector)
        element.click()
        return element

    def click_submit(self):
        """Click the first submit button of the page."""
        return self.click("button[type='submit']")

    def select_option(self, selector, value):
        """Select an option by its value in a native ``<select>``."""
        from selenium.webdriver.support.ui import Select

        Select(self.find(By.CSS_SELECTOR, selector)).select_by_value(value)

    def submit_form_via_js(self):
        """Submit the first form via JavaScript, bypassing HTML5 validation.

        Used by negative tests that must reach the server-side validation
        even when the browser would block the submission (required/min/max).
        """
        self.driver.execute_script("document.forms[0].submit();")

    def element_text(self, selector, default=""):
        """Return the text of an element, or ``default`` when it is absent."""
        try:
            return self.find(By.CSS_SELECTOR, selector, timeout=5).text
        except TimeoutException:
            return default

    def table_contains(self, value):
        """Return True when ``value`` appears inside the table body, if any."""
        try:
            tbody = self.find(By.CSS_SELECTOR, "tbody", timeout=3)
        except TimeoutException:
            return False
        return value in tbody.text
