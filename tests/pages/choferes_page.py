"""Page object for the choferes (drivers) module."""

from selenium.webdriver.common.by import By

from tests.pages.base_page import BasePage


class ChoferesPage(BasePage):
    """List, create, search and delete choferes."""

    def open_list(self):
        return self.open("/choferes")

    def open_new(self):
        return self.open("/choferes/new")

    def create(self, name, cedula, licencia="B", telefono=""):
        """Fill the new-chofer form and submit it."""
        self.open_new()
        self.fill("#name", name)
        self.fill("#cedula", cedula)
        self.select_option("#licencia", licencia)
        self.fill("#telefono", telefono)
        self.click_submit()
        return self

    @property
    def form_error(self):
        return self.element_text("#form-error")

    @property
    def flash_text(self):
        return self.element_text("#flash")

    def list_contains(self, name):
        return self.table_contains(name)

    def search(self, q):
        self.fill("input[name='q']", q)
        self.click("form.search-form button[type='submit']")
        return self

    def delete_by_name(self, name):
        """Delete the first row whose text contains ``name``."""
        for row in self.find_all(By.CSS_SELECTOR, "tbody tr"):
            if name in row.text:
                row.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                return True
        return False

    def has_new_link(self):
        return bool(self.find_all(By.CSS_SELECTOR, 'a[href="/choferes/new"]'))
