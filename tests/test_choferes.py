"""US-02: Choferes CRUD — happy path, negative and boundary cases."""

from tests.conftest import unique_suffix
from tests.pages.choferes_page import ChoferesPage


def test_create_chofer_happy_path(driver, login, base_url):
    """A valid chofer is created and appears in the list with a success flash."""
    login(driver, base_url, "admin", "admin123")
    page = ChoferesPage(driver, base_url)
    name = f"Chofer Feliz {unique_suffix()}"

    page.create(name, unique_suffix(), licencia="B", telefono="809-555-0100")

    page.wait_for_url_ends_with("/choferes")
    assert page.current_url.rstrip("/").endswith("/choferes")
    assert "Chofer creado" in page.flash_text
    assert page.list_contains(name)


def test_create_chofer_negative_empty_name(driver, login, base_url):
    """An empty name is rejected by the server-side validation."""
    login(driver, base_url, "admin", "admin123")
    page = ChoferesPage(driver, base_url)

    # A single space passes the browser's `required` check and lets the form
    # reach the server, which strips it and reports the validation error.
    page.create(" ", unique_suffix())

    page.wait_for_element("#form-error")
    assert page.current_url.rstrip("/").endswith("/choferes/new")
    assert page.form_error == "El nombre es obligatorio."


def test_create_chofer_boundary_name_too_long(driver, login, base_url):
    """A 201-character name exceeds the 200-character limit."""
    login(driver, base_url, "admin", "admin123")
    page = ChoferesPage(driver, base_url)

    page.create("A" * 201, unique_suffix())

    page.wait_for_element("#form-error")
    assert page.form_error == "El nombre no puede superar los 200 caracteres."


def test_create_chofer_negative_duplicate_cedula(driver, login, base_url):
    """Creating two choferes with the same cédula is rejected."""
    login(driver, base_url, "admin", "admin123")
    page = ChoferesPage(driver, base_url)
    cedula = unique_suffix()

    page.create(f"Chofer Uno {unique_suffix()}", cedula)
    page.wait_for_url_ends_with("/choferes")

    page.create(f"Chofer Dos {unique_suffix()}", cedula)

    page.wait_for_element("#form-error")
    assert page.form_error == "Ya existe un chofer con esa cédula."


def test_consultor_cannot_create(driver, login, base_url):
    """A read-only user is redirected away from the create form."""
    login(driver, base_url, "consultor", "consultor123")
    page = ChoferesPage(driver, base_url)

    page.open_new()
    page.wait_for_url_ends_with("/dashboard")
    assert page.current_url.rstrip("/").endswith("/dashboard")

    page.open_list()
    assert not page.has_new_link()
