"""US-01: Login — happy path, wrong credentials and empty fields."""

from tests.pages.login_page import LoginPage


def test_login_happy_path(driver, base_url):
    """Valid credentials land on the dashboard."""
    page = LoginPage(driver, base_url)
    page.open()
    page.login("admin", "admin123")
    page.wait_for_url_ends_with("/dashboard")
    assert page.current_url.rstrip("/").endswith("/dashboard")
    assert "Panel de control" in page.body_text


def test_login_wrong_password(driver, base_url):
    """Wrong password keeps the user on /login and shows the error message."""
    page = LoginPage(driver, base_url)
    page.open()
    page.login("admin", "wrongpass")
    page.wait_for_url_ends_with("/login")
    assert page.is_on_login()
    assert page.error_message == "Usuario o contraseña incorrectos"


def test_login_empty_fields(driver, base_url):
    """Submitting the empty form is blocked by the browser's required fields."""
    page = LoginPage(driver, base_url)
    page.open()
    page.click_submit()
    assert page.current_url.rstrip("/").endswith("/login")
