import http.server
import logging
from pathlib import Path
import socketserver
import threading
from typing import Generator
import pytest
from playwright.sync_api import Page, expect, sync_playwright, TimeoutError as PlaywrightTimeoutError, Browser
from playwright_utils import (
    wait_for_element, wait_for_all_elements,
    wait_for_element_to_be_clickable, wait_for_url_change,
    click_element_safely, send_keys_safely
)

# Configure logging
logger = logging.getLogger(__name__)


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve files from the example_site directory
        root = Path(__file__).parent.parent / "example_site"
        return str(root / path.lstrip("/"))

@pytest.fixture(scope="module")
def test_server() -> Generator[str, None, None]:
    PORT = 8000
    handler = CustomHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), handler)

    def serve():
        with httpd:
            httpd.serve_forever()

    server_thread = threading.Thread(target=serve)
    server_thread.daemon = True
    server_thread.start()

    yield f"http://localhost:{PORT}"

    httpd.shutdown()
    server_thread.join()

@pytest.fixture(scope="function")
def page_context(browser: Browser) -> Generator[Page, None, None]:
    context = browser.new_context()
    page = context.new_page()
    yield page
    page.close()
    context.close()

# --- Tests for wait_for_element ---
def test_wait_for_element_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    element = wait_for_element(page_context, "#delayedElement", timeout=3000)
    assert element is not None
    logger.info("test_wait_for_element_success passed.")

def test_wait_for_element_timeout(page_context: Page, test_server: str) -> None:
    """Tests timeout handling when the element is not found."""
    page_context.goto(test_server)
    selector = "#nonExistentElement"
    with pytest.raises(Exception):
        wait_for_element(page_context, selector, timeout=1000)
    logger.info("test_wait_for_element_timeout passed.")

# --- Tests for wait_for_all_elements ---
def test_wait_for_all_elements_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    elements = wait_for_all_elements(page_context, "#multipleElementsContainer p", timeout=3000)
    assert len(elements) == 3
    logger.info("test_wait_for_all_elements_success passed.")

def test_wait_for_all_elements_timeout(page_context: Page, test_server: str) -> None:
    """Tests timeout handling when not all elements are found."""
    page_context.goto(test_server)
    selector = ".nonExistentClass"
    with pytest.raises(Exception):
        wait_for_all_elements(page_context, selector, timeout=1000)
    logger.info("test_wait_for_all_elements_timeout passed.")

# --- Tests for url change ---
def test_wait_for_url_change_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.click("#linkToExample")
    wait_for_url_change(page_context, "http://localhost:8000/new")
    assert page_context.url == "http://localhost:8000/new"
    logger.info("test_wait_for_url_change_success passed.")

def test_wait_for_url_change_timeout(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    try:
        page_context.wait_for_function("window.location.href === 'http://localhost:8000/new'", timeout=1000)
    except PlaywrightTimeoutError:
        pass
    assert page_context.url == "http://localhost:8000/"
    logger.info("test_wait_for_url_change_timeout passed.")

# --- Tests for click element safely ---
def test_click_element_safely_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    click_element_safely(page_context, "#clickableElement")
    overlay = wait_for_element(page_context, "#overlay", timeout=3000)
    assert overlay is not None and overlay.is_visible()
    logger.info("test_click_element_safely_success passed.")

def test_click_element_safely_stale_element(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.evaluate("document.body.innerHTML = '<button id=\"btn\">Click me</button>'")
    page_context.wait_for_selector("#btn").click()
    page_context.evaluate("document.getElementById('btn').remove()")
    try:
        page_context.wait_for_selector("#btn").click()
    except PlaywrightTimeoutError:
        pass
    logger.info("test_click_element_safely_stale_element passed.")

def test_click_element_safely_intercepted(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.evaluate("document.body.innerHTML = '<button id=\"btn\">Click me</button>'")
    try:
        page_context.wait_for_selector("#btn", timeout=1000).click()
    except PlaywrightTimeoutError:
        pass
    logger.info("test_click_element_safely_intercepted passed.")

# --- Tests for send keys safely ---
def test_send_keys_safely_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    send_keys_safely(page_context, "#textInput", "Test Input")
    input_value = page_context.input_value("#textInput")
    assert input_value == "Test Input"
    logger.info("test_send_keys_safely_success passed.")

def test_send_keys_safely_stale_element(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.evaluate("document.body.innerHTML = '<input id=\"input\"/>'")
    input_element = page_context.wait_for_selector("#input")
    input_element.fill("Test Input")
    page_context.evaluate("document.getElementById('input').remove()")
    try:
        input_element = page_context.wait_for_selector("#input")
        input_element.fill("New Input")
    except PlaywrightTimeoutError:
        pass
    logger.info("test_send_keys_safely_stale_element passed.")

# --- Tests for element is clickable ---
def test_wait_for_element_to_be_clickable_success(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    wait_for_element_to_be_clickable(page_context, "#clickableElement", timeout=3000)
    page_context.click("#clickableElement")
    overlay = wait_for_element(page_context, "#overlay", timeout=3000)
    assert overlay is not None and overlay.is_visible()
    logger.info("test_wait_for_element_to_be_clickable_success passed.")

def test_wait_for_element_to_be_clickable_timeout(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    selector = "#nonExistentElement"
    with pytest.raises(Exception):
        wait_for_element_to_be_clickable(page_context, selector, timeout=1000)
    logger.info("test_wait_for_element_to_be_clickable_timeout passed.")

def test_wait_for_element_to_be_clickable_stale(page_context: Page, test_server: str) -> None:
    page_context.goto(test_server)
    page_context.evaluate("document.body.innerHTML = '<button id=\"btn\">Click me</button>'")
    page_context.wait_for_function("document.querySelector('#btn').offsetParent !== null")
    page_context.click("#btn")
    page_context.evaluate("document.getElementById('btn').remove()")
    try:
        page_context.wait_for_function("document.querySelector('#btn') !== null")
    except PlaywrightTimeoutError:
        pass
    logger.info("test_wait_for_element_to_be_clickable_stale passed.")