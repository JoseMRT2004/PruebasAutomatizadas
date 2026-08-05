"""Page object for the horas trabajadas (work hours) module."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from tests.pages.base_page import BasePage


class HorasPage(BasePage):
    """Register work hours and inspect the horas list."""

    def open_new(self):
        return self.open("/horas/new")

    def add_select_option(self, select_id, value):
        """Inject an option (creating it when missing) and select it by value.

        Needed for the negative test that must pick a chofer id that does not
        exist in the database (e.g. ``999999``).
        """
        self.driver.execute_script(
            """
            var sel = document.getElementById(arguments[0]);
            var opt = document.createElement('option');
            opt.value = arguments[1];
            opt.text = arguments[1];
            sel.appendChild(opt);
            sel.value = arguments[1];
            """,
            select_id,
            str(value),
        )

    def select_chofer_by_value(self, value):
        self.add_select_option("chofer_id", value)

    def select_ruta_by_value(self, value):
        self.add_select_option("ruta_id", value)

    def option_value_by_text(self, selector, text):
        """Return the value of the option whose visible text matches ``text``."""
        select = Select(self.find(By.CSS_SELECTOR, selector))
        for option in select.options:
            if option.text.strip() == text:
                return option.get_attribute("value")
        return ""

    def create(self, chofer_id, ruta_id, fecha, horas):
        """Fill the register-hours form and submit it."""
        self.open_new()
        self.select_chofer_by_value(chofer_id)
        self.select_ruta_by_value(ruta_id)
        self.fill("#fecha", fecha)
        self.fill("#horas", horas)
        self.click_submit()
        return self

    @property
    def form_error(self):
        return self.element_text("#form-error")

    @property
    def flash_text(self):
        return self.element_text("#flash")

    def list_contains(self, chofer_name):
        return self.table_contains(chofer_name)

    def delete_first(self):
        self.click("tbody tr button[type='submit']")
        return self
