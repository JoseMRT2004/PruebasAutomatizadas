"""US-03: Camiones CRUD — happy path, negative and boundary cases."""

from tests.conftest import unique_suffix
from tests.pages.camiones_page import CamionesPage


def test_create_camion_happy_path(driver, login, base_url):
    """A valid camión is created and appears in the list with a success flash."""
    login(driver, base_url, "admin", "admin123")
    page = CamionesPage(driver, base_url)
    placa = f"PLACA-{unique_suffix()}"

    page.create(placa, "Scania", "R500", "2024", "5000")

    page.wait_for_url_ends_with("/camiones")
    assert page.current_url.rstrip("/").endswith("/camiones")
    assert "Camión creado" in page.flash_text
    assert page.list_contains(placa)


def test_create_camion_negative_empty_placa(driver, login, base_url):
    """An empty placa is rejected by the server-side validation."""
    login(driver, base_url, "admin", "admin123")
    page = CamionesPage(driver, base_url)

    # Space passes the browser's `required` check so the server validation runs.
    page.create(" ", "Scania", "R500", "2024", "5000")

    page.wait_for_element("#form-error")
    assert page.current_url.rstrip("/").endswith("/camiones/new")
    assert page.form_error == "La placa es obligatoria."


def test_create_camion_boundary_duplicate_placa(driver, login, base_url):
    """Creating two camiones with the same placa is rejected."""
    login(driver, base_url, "admin", "admin123")
    page = CamionesPage(driver, base_url)
    placa = f"PLACA-{unique_suffix()}"

    page.create(placa, "Mack", "Anthem", "2023", "4500")
    page.wait_for_url_ends_with("/camiones")

    page.create(placa, "Volvo", "FH", "2022", "4800")

    page.wait_for_element("#form-error")
    assert page.form_error == "Ya existe un camión con esa placa."
