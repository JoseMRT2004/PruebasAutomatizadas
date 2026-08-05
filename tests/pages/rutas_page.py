"""Page object for the rutas (routes) module."""

from selenium.webdriver.common.by import By

from tests.pages.base_page import BasePage


class RutasPage(BasePage):
    """List, create, search and delete rutas."""

    def open_list(self):
        return self.open("/rutas")

    def open_new(self):
        return self.open("/rutas/new")

    def create(self, origen, destino, distancia_km, duracion_min):
        """Fill the new-ruta form and submit it."""
        self.open_new()
        self.fill("#origen", origen)
        self.fill("#destino", destino)
        self.fill("#distancia_km", distancia_km)
        self.fill("#duracion_min", duracion_min)
        self.click_submit()
        return self

    @property
    def form_error(self):
        return self.element_text("#form-error")

    @property
    def flash_text(self):
        return self.element_text("#flash")

    def list_contains(self, origen):
        return self.table_contains(origen)

    def search(self, q):
        self.fill("input[name='q']", q)
        self.click("form.search-form button[type='submit']")
        return self

    def delete_by_origen(self, origen):
        """Delete the first row whose text contains ``origen``."""
        for row in self.find_all(By.CSS_SELECTOR, "tbody tr"):
            if origen in row.text:
                row.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                return True
        return False

    def has_new_link(self):
        return bool(self.find_all(By.CSS_SELECTOR, 'a[href="/rutas/new"]'))
