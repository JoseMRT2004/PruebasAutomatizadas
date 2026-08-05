"""Shared fixtures and hooks for the Selenium test suite.

Responsible for:
- spawning the FastAPI app against a throwaway SQLite DB (session scope),
- providing a per-test Firefox WebDriver,
- capturing a screenshot per test scenario and attaching it to the HTML report,
- guaranteeing unique test data so every test is independent and rerunnable.
"""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from itertools import count
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
SCREENSHOTS_DIR = REPO_ROOT / "screenshots"

_HTML_AVAILABLE = False
_UNIQUE_COUNTER = count()


def unique_suffix() -> str:
    """Return a globally unique numeric-ish suffix for test data.

    Combines the current time with a process-wide counter so records created
    by different tests never collide, even on fast reruns.
    """
    return f"{int(time.time() * 1000)}{next(_UNIQUE_COUNTER)}"


def _sanitize_filename(value: str) -> str:
    """Turn a pytest nodeid into a safe file name."""
    return value.replace("/", "_").replace(":", "_").replace(" ", "_")


def _create_driver(retries: int = 3) -> webdriver.Firefox:
    """Build a configured Firefox WebDriver, retrying transient startup races.

    Defaults to HEADED so a demo video can record the run. Set HEADLESS=1 to
    run without a window. geckodriver is resolved automatically by Selenium
    Manager (Selenium >= 4.25) on first driver creation.

    Firefox occasionally fails to start a Marionette session under rapid
    sequential launches ("Failed to decode response from marionette"), so we
    retry a few times before giving up.
    """
    last_error = None
    for attempt in range(retries):
        try:
            options = Options()
            options.add_argument("--width=1280")
            options.add_argument("--height=900")
            if os.environ.get("HEADLESS") == "1":
                options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1280, 900)
            driver.implicitly_wait(10)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as exc:  # noqa: BLE001 - transient startup failures
            last_error = exc
            time.sleep(2 * (attempt + 1))
    raise last_error


def _login(driver, base_url: str, username: str, password: str):
    """Log in through the UI and wait until the dashboard is shown."""
    from tests.pages.login_page import LoginPage

    page = LoginPage(driver, base_url)
    page.open()
    page.login(username, password)
    page.wait_for_url_ends_with("/dashboard")
    return page


# --------------------------------------------------------------------------- server


@pytest.fixture(scope="session")
def server():
    """Start the app on a free port with a temp DB and yield its base URL."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    temp_dir = tempfile.mkdtemp(prefix="gestion-transporte-test-")
    db_path = os.path.join(temp_dir, "test.db")

    env = dict(os.environ)
    env["APP_DB_PATH"] = db_path

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 40
    while time.time() < deadline:
        if proc.poll() is not None:
            proc.wait()
            raise RuntimeError(f"app subprocess exited early (code {proc.returncode})")
        try:
            with urllib.request.urlopen(f"{base_url}/health", timeout=2) as response:
                if response.status == 200:
                    break
        except OSError:
            pass
        time.sleep(0.3)
    else:
        proc.terminate()
        raise RuntimeError("app did not become healthy within 40s")

    try:
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def base_url(server):
    return server


# --------------------------------------------------------------------------- driver / login


@pytest.fixture
def driver():
    """Per-test Firefox WebDriver."""
    driver_instance = _create_driver()
    yield driver_instance
    driver_instance.quit()


@pytest.fixture
def login():
    """Return a callable that logs in through the UI and asserts the dashboard."""
    return _login


@pytest.fixture(scope="module")
def horas_setup(server):
    """Create a chofer and a ruta through the UI once per module.

    Returns their database ids (read from the /horas/new select options) plus
    the chofer name, so every horas test can reference valid records.
    """
    from tests.pages.choferes_page import ChoferesPage
    from tests.pages.horas_page import HorasPage
    from tests.pages.rutas_page import RutasPage

    driver_instance = _create_driver()
    try:
        _login(driver_instance, server, "admin", "admin123")

        suffix = unique_suffix()
        chofer_name = f"Chofer E2E {suffix}"
        cedula = str(int(suffix))
        destino = f"Destino E2E {suffix}"

        choferes = ChoferesPage(driver_instance, server)
        choferes.create(chofer_name, cedula)
        choferes.wait_for_url_ends_with("/choferes")

        rutas = RutasPage(driver_instance, server)
        rutas.create(f"Origen E2E {suffix}", destino, "150", "90")
        rutas.wait_for_url_ends_with("/rutas")

        horas = HorasPage(driver_instance, server)
        horas.open_new()
        ruta_label = f"Origen E2E {suffix} → {destino}"
        chofer_id = horas.option_value_by_text("#chofer_id", chofer_name)
        ruta_id = horas.option_value_by_text("#ruta_id", ruta_label)

        assert chofer_id, "chofer option not found in /horas/new"
        assert ruta_id, "ruta option not found in /horas/new"

        return {
            "chofer_id": chofer_id,
            "ruta_id": ruta_id,
            "chofer_name": chofer_name,
        }
    finally:
        driver_instance.quit()


# --------------------------------------------------------------------------- report / screenshots


@pytest.fixture(scope="session", autouse=True)
def _prepare_output_dirs():
    """Ensure reports/ and screenshots/ exist before anything else runs."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def pytest_sessionstart(session):
    """Detect pytest-html availability and prepare output directories."""
    global _HTML_AVAILABLE
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import pytest_html  # noqa: F401
        from pytest_html import extras  # noqa: F401

        _HTML_AVAILABLE = True
    except Exception:
        _HTML_AVAILABLE = False


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot per scenario and attach it to the HTML report."""
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    driver_instance = item.funcargs.get("driver")
    if driver_instance is None:
        return

    name = f"{_sanitize_filename(item.nodeid)}_{report.outcome}.png"
    screenshot_path = SCREENSHOTS_DIR / name
    try:
        driver_instance.save_screenshot(str(screenshot_path))
    except Exception:
        return

    if not _HTML_AVAILABLE:
        return

    try:
        from pytest_html import extras

        # Relative to reports/, so the <img src> resolves from report.html.
        relative_path = os.path.relpath(str(screenshot_path), str(REPORTS_DIR))
        extras_list = getattr(report, "extras", [])
        extras_list.append(extras.image(relative_path))
        report.extras = extras_list
    except Exception:
        pass
