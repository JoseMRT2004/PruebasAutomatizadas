"""US-05: Registro de horas — happy path, negative and boundary cases.

The ``horas_setup`` fixture (in conftest.py) creates one chofer and one ruta
through the UI and exposes their ids so every test references valid records.
"""

import pytest

from tests.pages.horas_page import HorasPage

FECHA = "2026-08-05"


def test_register_horas_happy_path(driver, login, base_url, horas_setup):
    """Registering 8 horas creates a record with a success flash."""
    login(driver, base_url, "admin", "admin123")
    page = HorasPage(driver, base_url)

    page.create(horas_setup["chofer_id"], horas_setup["ruta_id"], FECHA, "8")

    page.wait_for_url_ends_with("/horas")
    assert page.current_url.rstrip("/").endswith("/horas")
    assert "Horas registradas" in page.flash_text
    assert page.list_contains(horas_setup["chofer_name"])


def test_register_horas_negative_chofer_inexistente(driver, login, base_url, horas_setup):
    """A chofer id that does not exist is rejected by the server validation."""
    login(driver, base_url, "admin", "admin123")
    page = HorasPage(driver, base_url)

    page.create("999999", horas_setup["ruta_id"], FECHA, "8")

    page.wait_for_element("#form-error")
    assert page.form_error == "El chofer seleccionado no existe."


@pytest.mark.parametrize("bad_horas", [0, 25])
def test_register_horas_boundary_invalid(driver, login, base_url, horas_setup, bad_horas):
    """0 and 25 horas are out of range and must be rejected.

    The browser's min/max attributes would block the submission, so the form
    is submitted via JavaScript to reach the server-side validation.
    """
    login(driver, base_url, "admin", "admin123")
    page = HorasPage(driver, base_url)

    page.open_new()
    page.select_chofer_by_value(horas_setup["chofer_id"])
    page.select_ruta_by_value(horas_setup["ruta_id"])
    page.fill("#fecha", FECHA)
    page.fill("#horas", bad_horas)
    page.submit_form_via_js()

    page.wait_for_element("#form-error")
    assert page.form_error == "Las horas deben estar entre 1 y 24."


def test_register_horas_boundary_max_24_ok(driver, login, base_url, horas_setup):
    """24 horas is the maximum allowed and must be accepted."""
    login(driver, base_url, "admin", "admin123")
    page = HorasPage(driver, base_url)

    page.create(horas_setup["chofer_id"], horas_setup["ruta_id"], FECHA, "24")

    page.wait_for_url_ends_with("/horas")
    assert "Horas registradas" in page.flash_text
    assert page.list_contains(horas_setup["chofer_name"])
