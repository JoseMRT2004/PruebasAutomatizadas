"""Page object for the camiones (trucks) module."""

from selenium.webdriver.common.by import By

from tests.pages.base_page import BasePage


class CamionesPage(BasePage):
    """List, create, search and delete camiones."""

    def open_list(self):
        return self.open("/camiones")

    def open_new(self):
        return self.open("/camiones/new")

    def create(self, placa, marca, modelo, anio, capacidad):
        """Fill the new-camion form and submit it."""
        self.open_new()
        self.fill("#placa", placa)
        self.fill("#marca", marca)
        self.fill("#modelo", modelo)
        self.fill("#anio", anio)
        self.fill("#capacidad", capacidad)
        self.click_submit()
        return self

    @property
    def form_error(self):
        return self.element_text("#form-error")

    @property
    def flash_text(self):
        return self.element_text("#flash")

    def list_contains(self, placa):
        return self.table_contains(placa)

    def search(self, q):
        self.fill("input[name='q']", q)
        self.click("form.search-form button[type='submit']")
        return self

    def delete_by_placa(self, placa):
        """Delete the first row whose text contains ``placa``."""
        for row in self.find_all(By.CSS_SELECTOR, "tbody tr"):
            if placa in row.text:
                row.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                return True
        return False

    def has_new_link(self):
        return bool(self.find_all(By.CSS_SELECTOR, 'a[href="/camiones/new"]'))
