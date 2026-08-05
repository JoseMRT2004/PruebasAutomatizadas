"""US-04: Rutas CRUD — happy path, negative and boundary cases."""

from tests.conftest import unique_suffix
from tests.pages.rutas_page import RutasPage


def test_create_ruta_happy_path(driver, login, base_url):
    """A valid ruta is created and appears in the list with a success flash."""
    login(driver, base_url, "admin", "admin123")
    page = RutasPage(driver, base_url)
    origen = f"SDQ-{unique_suffix()}"

    page.create(origen, "STI", "150", "120")

    page.wait_for_url_ends_with("/rutas")
    assert page.current_url.rstrip("/").endswith("/rutas")
    assert "Ruta creada" in page.flash_text
    assert page.list_contains(origen)


def test_create_ruta_negative_empty_origen(driver, login, base_url):
    """An empty origen is rejected by the server-side validation."""
    login(driver, base_url, "admin", "admin123")
    page = RutasPage(driver, base_url)

    # Space passes the browser's `required` check so the server validation runs.
    page.create(" ", "STI", "150", "120")

    page.wait_for_element("#form-error")
    assert page.current_url.rstrip("/").endswith("/rutas/new")
    assert page.form_error == "El origen es obligatorio."


def test_create_ruta_boundary_distancia_zero(driver, login, base_url):
    """A distance of 0 km is rejected (must be greater than 0)."""
    login(driver, base_url, "admin", "admin123")
    page = RutasPage(driver, base_url)

    page.create(f"SDQ-{unique_suffix()}", "STI", "0", "120")

    page.wait_for_element("#form-error")
    assert page.form_error == "La distancia debe ser mayor que 0 y no superar 5000 km."
